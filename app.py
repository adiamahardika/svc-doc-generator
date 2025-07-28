from application import Application

# Create application instance
app_instance = Application()
app = app_instance.create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
