#!/usr/bin/env python3.6
from app import create_app
# main entry point.
application = create_app()
if __name__ == '__main__':
    # Entry point when run via Python interpreter.
    print("== Running in debug mode ==")
    application.run(host='localhost', port=8080, debug=True)