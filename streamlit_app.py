TypeError: This app has encountered an error. The original error message is redacted to prevent data leaks. Full error details have been recorded in the logs (if you're on Streamlit Cloud, click on 'Manage app' in the lower right of your app).
Traceback:
File "/mount/src/prova/streamlit_app.py", line 177, in <module>
    main()
    ~~~~^^
File "/mount/src/prova/streamlit_app.py", line 112, in main
    login_google()
    ~~~~~~~~~~~~^^
File "/mount/src/prova/streamlit_app.py", line 93, in login_google
    oauth2 = OAuth2Component(
        client_id=GOOGLE_CLIENT_ID,
    ...<4 lines>...
        scope=["openid", "email", "profile"]
