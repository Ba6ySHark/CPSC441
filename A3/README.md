# Panda Chat

## How to run the App

Since I decided to add random name generation and UI for client side of the application, there are 2 dependencies that so not come with python out of the box.

To install them, I suggest to create a virtual environment:

```bash
pip install virtualenv
```

```bash
virtualenv myenv
```

```bash
myenv/Scripts/activate # if on Windows
source myenv/bin/activate # if on Linux or MacOS
```

Then, install the dependecies:

```bash
pip install -r requirements.txt
```

Finally, run Client.py and Server.py in separate <i>cmd</i> instances:

```bash
python Server.py
```
AND
```bash
python Client.py
```

## File structure & design decisions

File Structure:
<ul>
    <li><i>myenv</i> - contains project dependencies files</li>
    <li><i>requirements.txt</i> - containes project dependencies names</li>
    <li><i>server_log.txt</i> - sample server logs</li>
    <li><i>Server.py</i> - source code for the server side</li>
    <li><i>Client.py</i> - source code for cient side</li>
</ul>

Design choices:
I decided to divide source code for the client side into Logic and UI part to allow for better code readability and encapsulation. The server side source code is also wrapped in a parent class.

## Extra Features

### UI
Simple UI that allows users to connect to the server and chat with other pandas in the groove.

### Random name generation
Initially the user is offered a randomly generated name that he can edit or delete entirely. Implemented via <i>coolname</i> package.