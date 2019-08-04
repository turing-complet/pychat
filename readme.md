Bad implementation of two party chat

Start the server: `python server.py`. Port is hard coded in the file.

Start a client and connect with a username. `python client.py -s localhost -u <your-username>`
The port is also hard coded here.

Chat with a user `/chat <other-user>`. If the user isn't connected yet, it will queue any messages you send. They must also send you a `/chat` command for a session to be created.
