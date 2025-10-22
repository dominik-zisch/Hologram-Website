from app import create_app
# from rfid_listener import start_listener

app = create_app()

if __name__ == "__main__":
    # start_listener()
    app.run(debug=False, host="0.0.0.0", port=5050)

