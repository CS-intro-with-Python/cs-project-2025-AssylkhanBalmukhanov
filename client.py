import requests
import sys
import os

BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")


def test_endpoint(endpoint, description, expected_text=None):
    """
    Tests a given endpoint on the server.
    Exits with error code 1 if the test fails.
    """
    try:
        url = f"{BASE_URL}{endpoint}"
        print(f"--- {description} ---")
        print(f"Requesting URL: {url}")

        response = requests.get(url, timeout=10)

        response.raise_for_status()

        print(f"Status Code: {response.status_code} (Success)")

        # Check if the response text contains the expected content
        if expected_text:
            if expected_text in response.text:
                print(f"Success: Found expected text '{expected_text}' in response.")
            else:
                print(f"Error: Did not find expected text '{expected_text}' in response.")
                print(f"Response Text (first 500 chars): {response.text[:500]}...")
                sys.exit(1)

        print("Route check successful.\n")

    except requests.exceptions.RequestException as e:
        print(f"Error: Could not connect to the server at {BASE_URL}.")
        print("Is the Docker container running and port 5000 exposed?")
        print(f"Details: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_endpoint(
        endpoint="/",
        description="Testing Root Route: /",
        expected_text="Server is running! API and Docker are verified."
    )

    print("All client tests passed")