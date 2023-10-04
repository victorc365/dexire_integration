# EREBOTS 3.0

EREBOTS 3.0 is a scenario and platform agnostic multi-agent chatbot system. Able to implement different sets of behaviors and functions.

## Requirements

- [ ] Multi-Agent System (MAS)
  - [x] choose MAS System
  - [x] create basic implementation
    - [x] Start fastAPI at startup
    - [x] Start SPADE engine
    - [x] Create DFAgent
    - [x] Create AMSAgent
  - [x] create Gateway Agent
    - [x] Gateway handle personalized agent subscription
    - [x] Gateway handle websockets
    - [x] Gateway forward messages to personalized agent router
    - [x] Gateway forward messages to frontend
    - [x] Gateway handle agnostic formatting of messages
  - [ ] create Personalized Agent
    -  [x] Create Message Router Behaviour
    -  [ ] Create Contextual FSM
    -  [x] Create Profiling FSM 
    -  [ ] Create Persuasion FSM
  - [ ] simultaneous users

- [ ] Integration with Pryv
  - [x] registration
  - [x] authentication
  - [ ] data storage
  - [ ] data update
  - [ ] data retrieval
  - [x] data consent

- [ ] Front-end in Flutter
  - [x] Pryv / Erebots authentication
  - [ ] basic chat interface
    - [x] Create UI without custom keyboard, button, etc.  
    - [x] Create websocket connection with backend
    - [x] Sending message to backend
    - [ ] Customize UI
    - [ ] Receive  messages
  - [x] bot selection screen
  - [ ] profile screen

## Installation

## Environment Variables

### MongoDB Database Configuration

| Name                        | Project               | Description                                                             |
|-----------------------------|-----------------------|-------------------------------------------------------------------------|
| MONGODB_USER                | CORE                  | Username to connect to mongoDB                                          |
| MONGODB_PASSWORD            | CORE                  | User password to connect to mongoDB                                     |
| MONGODB_PORT                | CORE                  | Port on which mongoDB is exposed by the container.                      |

### Mongo Express Configuration

| Name                        | Project               | Description                                                             |
|-----------------------------|-----------------------|-------------------------------------------------------------------------|
| MONGO_EXPRESS_USER          | DEV TOOLS             | Username to connect to mongo express web interface                      |
| MONGO_EXPRESS_PASSWORD      | DEV TOOLS             | Password to connect to mongo express web interface                      |
| MONGO_EXPRESS_PORT          | DEV TOOLS             | Port on which mongo express web interface is exposed by the container   |

### XMPP Configuation

| Name            | Project               | Description                                                   |
|-----------------|-----------------------|---------------------------------------------------------------|
| XMPP_SERVER_URL | CORE                  | URL of the XMPP server used for prosody                       |
| XMPP_ADMIN_PORT | CORE                  | Port to connect to admin web interface. By default 9090       |
| XMPP_USER_PORT  | CORE                  | Port used for message exchange between users. By default 5222 |
| XMPP_SECRET_KEY | CORE                  | Secret key configured to access the user management rest API  |


### Log Configuration

| Name                        | Project               | Description                                                             |
|-----------------------------|-----------------------|-------------------------------------------------------------------------|
| LOG_DIRECTORY_PATH          | CORE                  | Path to the directory where to store logs in the container              |
| HOST_LOG_DIRECTORY_PATH     | CORE                  | Path to the directory where the logs are stored on the host system.     |
| LOG_LEVEL                   | CORE                  | Level of the log system. Can be INFO / WARNING / ERROR / DEBUG          |

### Pryv Database Configuration

| Name                         | Project               | Description                                       |
|------------------------------|-----------------------|---------------------------------------------------|
| PRYV_SERVER_URL              | CORE                  | Base URL to access Pryv API                       |
| PRYV_PROJECT_ID              | CORE                  | Name of the application in pryv                   | 

### Miscellaneous

| Name                       | Project | Description                                                                     |
|----------------------------|---------|---------------------------------------------------------------------------------|
| SPADE_PORT                 | CORE    | Port where the API of erebot is listening                                       |
| MODULE_DIRECTORY_PATH      | CUSTOM  | Directory containing the custom FSMs configuration known as "bots" for the user |
| MAXIMUM_CLIENT_PER_GATEWAY | CORE    | Maximum number of active websocket connection per gateway agent                 |
