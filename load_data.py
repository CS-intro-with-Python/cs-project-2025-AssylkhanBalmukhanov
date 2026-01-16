import csv
from app import app, db, ChessPosition


def load_positions_from_csv(filename='data/puzzles.csv'):
    """Load chess positions from CSV file into database"""
    with app.app_context():
        # Clear existing positions
        ChessPosition.query.delete()

        count = 0
        with open(filename, 'r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip header if present

            for row in csv_reader:
                if len(row) >= 3:
                    fen = row[0].strip()
                    evaluation = 0.0
                    piece_count = int(row[2])

                    position = ChessPosition(
                        fen=fen,
                        evaluation=evaluation,
                        piece_count=piece_count
                    )
                    db.session.add(position)
                    count += 1

                    if count % 100 == 0:
                        print(f"Loaded {count} positions...")

        db.session.commit()
        print(f"Successfully loaded {count} positions into database")

        # Print statistics
        for pc in range(2, 33):
            count_pc = ChessPosition.query.filter_by(piece_count=pc).count()
            if count_pc > 0:
                print(f"  {pc} pieces: {count_pc} positions")


if __name__ == '__main__':
    import sys

    filename = sys.argv[1] if len(sys.argv) > 1 else 'data/puzzles.csv'
    load_positions_from_csv(filename)