from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import random
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///chess_memory.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')

# Database setup
db = SQLAlchemy(app)

# Logger setup
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
app.logger.addHandler(handler)


# Models
class ChessPosition(db.Model):
    __tablename__ = 'chess_positions'
    id = db.Column(db.Integer, primary_key=True)
    fen = db.Column(db.String(100), nullable=False)
    evaluation = db.Column(db.Float)
    piece_count = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'fen': self.fen,
            'evaluation': self.evaluation,
            'piece_count': self.piece_count
        }


class GameSession(db.Model):
    __tablename__ = 'game_sessions'
    id = db.Column(db.Integer, primary_key=True)
    piece_count = db.Column(db.Integer, nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey('chess_positions.id'))
    user_answer = db.Column(db.String(100))
    score = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'piece_count': self.piece_count,
            'position_id': self.position_id,
            'user_answer': self.user_answer,
            'score': self.score,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


# Routes
@app.route('/')
def index():
    app.logger.info('Index page accessed')
    return render_template('index.html')


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for CI/CD"""
    app.logger.info('Health check accessed')
    return jsonify({'status': 'healthy', 'message': 'Application is running'}), 200


@app.route('/api/positions', methods=['GET'])
def get_positions():
    """Get all chess positions"""
    app.logger.info('Fetching all positions')
    try:
        positions = ChessPosition.query.all()
        return jsonify([pos.to_dict() for pos in positions]), 200
    except Exception as e:
        app.logger.error(f'Error fetching positions: {str(e)}')
        return jsonify({'error': 'Failed to fetch positions'}), 500


@app.route('/api/positions/count/<int:piece_count>', methods=['GET'])
def get_positions_by_count(piece_count):
    """Get positions by piece count"""
    app.logger.info(f'Fetching positions with {piece_count} pieces')
    try:
        if piece_count < 2 or piece_count > 32:
            app.logger.warning(f'Invalid piece count: {piece_count}')
            return jsonify({'error': 'Piece count must be between 2 and 32'}), 400

        positions = ChessPosition.query.filter_by(piece_count=piece_count).all()
        return jsonify([pos.to_dict() for pos in positions]), 200
    except Exception as e:
        app.logger.error(f'Error fetching positions by count: {str(e)}')
        return jsonify({'error': 'Failed to fetch positions'}), 500


@app.route('/api/game/start', methods=['POST'])
def start_game():
    """Start a new game session"""
    app.logger.info('Starting new game session')
    try:
        data = request.get_json()

        if not data or 'piece_count' not in data:
            app.logger.warning('Missing piece_count in request')
            return jsonify({'error': 'piece_count is required'}), 400

        piece_count = data['piece_count']

        if not isinstance(piece_count, int) or piece_count < 2 or piece_count > 32:
            app.logger.warning(f'Invalid piece count: {piece_count}')
            return jsonify({'error': 'piece_count must be an integer between 2 and 32'}), 400

        # Get random position with specified piece count
        positions = ChessPosition.query.filter_by(piece_count=piece_count).all()

        if not positions:
            app.logger.warning(f'No positions found for piece count: {piece_count}')
            return jsonify({'error': f'No positions available for {piece_count} pieces'}), 404

        selected_position = random.choice(positions)

        # Create game session
        session = GameSession(
            piece_count=piece_count,
            position_id=selected_position.id
        )
        db.session.add(session)
        db.session.commit()

        app.logger.info(f'Game session {session.id} created with position {selected_position.id}')

        return jsonify({
            'session_id': session.id,
            'fen': selected_position.fen,
            'piece_count': piece_count
        }), 201

    except Exception as e:
        app.logger.error(f'Error starting game: {str(e)}')
        db.session.rollback()
        return jsonify({'error': 'Failed to start game'}), 500


@app.route('/api/game/submit', methods=['POST'])
def submit_answer():
    """Submit user's answer and get score"""
    app.logger.info('Submitting answer')
    try:
        data = request.get_json()

        if not data or 'session_id' not in data or 'user_fen' not in data:
            app.logger.warning('Missing required fields in submit request')
            return jsonify({'error': 'session_id and user_fen are required'}), 400

        session_id = data['session_id']
        user_fen = data['user_fen']

        session = GameSession.query.get(session_id)
        if not session:
            app.logger.warning(f'Session not found: {session_id}')
            return jsonify({'error': 'Session not found'}), 404

        original_position = ChessPosition.query.get(session.position_id)

        # Calculate score (number of correct pieces)
        score = calculate_score(original_position.fen, user_fen)

        session.user_answer = user_fen
        session.score = score
        db.session.commit()

        app.logger.info(f'Answer submitted for session {session_id}, score: {score}')

        return jsonify({
            'score': score,
            'total_pieces': session.piece_count,
            'correct_fen': original_position.fen,
            'user_fen': user_fen,
            'differences': get_differences(original_position.fen, user_fen)
        }), 200

    except Exception as e:
        app.logger.error(f'Error submitting answer: {str(e)}')
        db.session.rollback()
        return jsonify({'error': 'Failed to submit answer'}), 500


@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Get all game sessions"""
    app.logger.info('Fetching all sessions')
    try:
        sessions = GameSession.query.order_by(GameSession.created_at.desc()).limit(100).all()
        return jsonify([s.to_dict() for s in sessions]), 200
    except Exception as e:
        app.logger.error(f'Error fetching sessions: {str(e)}')
        return jsonify({'error': 'Failed to fetch sessions'}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get game statistics"""
    app.logger.info('Fetching statistics')
    try:
        total_games = GameSession.query.filter(GameSession.score.isnot(None)).count()

        if total_games > 0:
            # Calculate percentage: (correct pieces / total pieces) * 100
            sessions = GameSession.query.filter(GameSession.score.isnot(None)).all()
            total_correct = sum(s.score for s in sessions)
            total_pieces = sum(s.piece_count for s in sessions)
            avg_percentage = (total_correct / total_pieces * 100) if total_pieces > 0 else 0
        else:
            avg_percentage = 0

        return jsonify({
            'total_games': total_games,
            'average_score': round(avg_percentage, 2)
        }), 200
    except Exception as e:
        app.logger.error(f'Error fetching stats: {str(e)}')
        return jsonify({'error': 'Failed to fetch statistics'}), 500


# Helper functions
def calculate_score(correct_fen, user_fen):
    """Calculate score based on correct pieces placement"""
    correct_board = fen_to_board(correct_fen)
    user_board = fen_to_board(user_fen)

    score = 0
    for i in range(8):
        for j in range(8):
            if correct_board[i][j] == user_board[i][j]:
                if correct_board[i][j] != '.':  # Only count pieces, not empty squares
                    score += 1

    return score


def fen_to_board(fen):
    """Convert FEN to 8x8 board representation"""
    board = []
    fen_board = fen.split()[0]

    for row in fen_board.split('/'):
        board_row = []
        for char in row:
            if char.isdigit():
                board_row.extend(['.'] * int(char))
            else:
                board_row.append(char)
        board.append(board_row)

    return board


def get_differences(correct_fen, user_fen):
    """Get list of differences between correct and user positions"""
    correct_board = fen_to_board(correct_fen)
    user_board = fen_to_board(user_fen)

    differences = []
    for i in range(8):
        for j in range(8):
            if correct_board[i][j] != user_board[i][j]:
                differences.append({
                    'square': f"{chr(97 + j)}{8 - i}",
                    'correct': correct_board[i][j],
                    'user': user_board[i][j]
                })

    return differences


# Initialize database
with app.app_context():
    db.create_all()
    app.logger.info('Database initialized')

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.getenv('FLASK_ENV') == 'development')