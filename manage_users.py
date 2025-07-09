import sys
from flask import Flask
from app import create_app
from app.admin_utils import delete_user_by_username, resend_verification


def main():
    if len(sys.argv) < 3:
        print("Usage: python manage_users.py [delete|resend] <username>")
        sys.exit(1)

    command = sys.argv[1]
    username = sys.argv[2]

    app = create_app()
    with app.app_context():
        if command == 'delete':
            result = delete_user_by_username(username)
        elif command == 'resend':
            result = resend_verification(username)
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
        print(result)

if __name__ == '__main__':
    main()
