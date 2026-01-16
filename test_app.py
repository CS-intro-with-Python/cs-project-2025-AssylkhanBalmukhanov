import pytest
import json
from app import app, db, ChessPosition, GameSession


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # Add test data
            test_position = ChessPosition(
                fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                evaluation=0.0,
                piece_count=32
            )
            db.session.add(test_position)
            db.session.commit()
        yield client
        with app.app_context():
            db.drop_all()


# Unit Tests
class TestInputValidation:
    """Unit tests for input validation"""

    def test_start_game_missing_piece_count(self, client):
        """Test start game with missing piece_count"""
        response = client.post('/api/game/start',
                               data=json.dumps({}),
                               content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'piece_count is required' in data['error']

    def test_start_game_invalid_piece_count_type(self, client):
        """Test start game with invalid piece_count type"""
        response = client.post('/api/game/start',
                               data=json.dumps({'piece_count': 'invalid'}),
                               content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_start_game_piece_count_out_of_range(self, client):
        """Test start game with piece_count out of valid range"""
        response = client.post('/api/game/start',
                               data=json.dumps({'piece_count': 50}),
                               content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'between 2 and 32' in data['error']

    def test_submit_answer_missing_fields(self, client):
        """Test submit answer with missing required fields"""
        response = client.post('/api/game/submit',
                               data=json.dumps({'session_id': 1}),
                               content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'required' in data['error']


class TestErrorHandling:
    """Unit tests for error handling"""

    def test_get_positions_by_invalid_count(self, client):
        """Test getting positions with invalid piece count"""
        response = client.get('/api/positions/count/100')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_submit_answer_nonexistent_session(self, client):
        """Test submitting answer for non-existent session"""
        response = client.post('/api/game/submit',
                               data=json.dumps({
                                   'session_id': 99999,
                                   'user_fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
                               }),
                               content_type='application/json')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'not found' in data['error'].lower()

    def test_start_game_no_positions_available(self, client):
        """Test starting game when no positions available for piece count"""
        response = client.post('/api/game/start',
                               data=json.dumps({'piece_count': 5}),
                               content_type='application/json')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data


# Integration Tests
class TestGameFlow:
    """Integration tests for complete game flow"""

    def test_complete_game_flow(self, client):
        """Test complete game flow from start to submit"""
        # Start game
        start_response = client.post('/api/game/start',
                                     data=json.dumps({'piece_count': 32}),
                                     content_type='application/json')
        assert start_response.status_code == 201
        start_data = json.loads(start_response.data)
        assert 'session_id' in start_data
        assert 'fen' in start_data
        assert start_data['piece_count'] == 32

        session_id = start_data['session_id']

        # Submit answer
        submit_response = client.post('/api/game/submit',
                                      data=json.dumps({
                                          'session_id': session_id,
                                          'user_fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
                                      }),
                                      content_type='application/json')
        assert submit_response.status_code == 200
        submit_data = json.loads(submit_response.data)
        assert 'score' in submit_data
        assert 'total_pieces' in submit_data
        assert 'correct_fen' in submit_data
        assert 'differences' in submit_data

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'


class TestAPIEndpoints:
    """Integration tests for API endpoints"""

    def test_get_all_positions(self, client):
        """Test getting all positions"""
        response = client.get('/api/positions')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0

    def test_get_positions_by_count(self, client):
        """Test getting positions by piece count"""
        response = client.get('/api/positions/count/32')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_sessions(self, client):
        """Test getting all sessions"""
        response = client.get('/api/sessions')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    def test_get_stats(self, client):
        """Test getting statistics"""
        response = client.get('/api/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_games' in data
        assert 'average_score' in data

    def test_index_route(self, client):
        """Test index route returns HTML"""
        response = client.get('/')
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main(['-v', __file__])