from app import create_app

if __name__ == '__main__':
    uscp_app = create_app()
    uscp_app.run(debug=True)