import requests
import json
import sys


class ChessMemoryClient:
    def __init__(self, base_url='http://localhost:5000'):
        self.base_url = base_url

    def check_health(self):
        """Check if the server is healthy"""
        try:
            response = requests.get(f'{self.base_url}/health')
            if response.status_code == 200:
                print("✓ Health check passed")
                print(f"  Response: {response.json()}")
                return True
            else:
                print(f"✗ Health check failed with status {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Health check failed: {str(e)}")
            return False

    def get_positions(self):
        """Get all positions"""
        try:
            response = requests.get(f'{self.base_url}/api/positions')
            if response.status_code == 200:
                positions = response.json()
                print(f"✓ Retrieved {len(positions)} positions")
                return True
            else:
                print(f"✗ Failed to get positions: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error getting positions: {str(e)}")
            return False

    def get_positions_by_count(self, count=32):
        """Get positions by piece count"""
        try:
            response = requests.get(f'{self.base_url}/api/positions/count/{count}')
            if response.status_code == 200:
                positions = response.json()
                print(f"✓ Retrieved {len(positions)} positions with {count} pieces")
                return True
            else:
                print(f"✗ Failed to get positions by count: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error getting positions by count: {str(e)}")
            return False

    def start_game(self, piece_count=32):
        """Start a new game"""
        try:
            response = requests.post(
                f'{self.base_url}/api/game/start',
                json={'piece_count': piece_count}
            )
            if response.status_code == 201:
                data = response.json()
                print(f"✓ Game started successfully")
                print(f"  Session ID: {data['session_id']}")
                print(f"  FEN: {data['fen']}")
                return data
            else:
                print(f"✗ Failed to start game: {response.status_code}")
                print(f"  Response: {response.json()}")
                return None
        except Exception as e:
            print(f"✗ Error starting game: {str(e)}")
            return None

    def submit_answer(self, session_id, user_fen):
        """Submit answer for a game"""
        try:
            response = requests.post(
                f'{self.base_url}/api/game/submit',
                json={
                    'session_id': session_id,
                    'user_fen': user_fen
                }
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Answer submitted successfully")
                print(f"  Score: {data['score']}/{data['total_pieces']}")
                print(f"  Differences: {len(data['differences'])}")
                return data
            else:
                print(f"✗ Failed to submit answer: {response.status_code}")
                print(f"  Response: {response.json()}")
                return None
        except Exception as e:
            print(f"✗ Error submitting answer: {str(e)}")
            return None

    def get_stats(self):
        """Get game statistics"""
        try:
            response = requests.get(f'{self.base_url}/api/stats')
            if response.status_code == 200:
                stats = response.json()
                print(f"✓ Statistics retrieved")
                print(f"  Total games: {stats['total_games']}")
                print(f"  Average score: {stats['average_score']}")
                return True
            else:
                print(f"✗ Failed to get stats: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error getting stats: {str(e)}")
            return False

    def run_all_checks(self):
        """Run all route checks"""
        print("=" * 50)
        print("Running all route checks...")
        print("=" * 50)

        results = []

        print("\n1. Health Check")
        results.append(self.check_health())

        print("\n2. Get All Positions")
        results.append(self.get_positions())

        print("\n3. Get Positions by Count")
        results.append(self.get_positions_by_count(32))

        print("\n4. Get Statistics")
        results.append(self.get_stats())

        print("\n" + "=" * 50)
        passed = sum(results)
        total = len(results)
        print(f"Results: {passed}/{total} checks passed")
        print("=" * 50)

        return all(results)


def main():
    base_url = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:5000'

    client = ChessMemoryClient(base_url)
    success = client.run_all_checks()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
