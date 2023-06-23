# EREBOTS 3.0

EREBOTS 3.0 is a scenario and platform agnostic  multi-agent chatbot system. Able to implement different sets of behaviors and functions.

## Installation

## Environment Variables

| Name                        | Project               | Description                                                             |
|-----------------------------|-----------------------|-------------------------------------------------------------------------|
| MONGODB_USER                | CORE                  | Username to connect to mongoDB                                          |
| MONGODB_PASSWORD            | CORE                  | User password to connect to mongoDB                                     |
| MONGODB_PORT                | CORE                  | Port on which mongoDB is exposed by the container.                      |
|                             |                       |                                                                         |
| MONGO_EXPRESS_USER          | DEV TOOLS             | Username to connect to mongo express web interface                      |
| MONGO_EXPRESS_PASSWORD      | DEV TOOLS             | Password to connect to mongo express web interface                      |
| MONGO_EXPRESS_PORT          | DEV TOOLS             | Port on which mongo express web interface is exposed by the container   |
|                             |                       |                                                                         |
| XMPP_SERVER_URL             | CORE                  | URL of the XMPP server used for prosody                                 |
| XMPP_SERVER_PASS            | CORE                  | Password to connect to the XMPP server                                  |
|                             |                       |                                                                         |
| LOG_DIRECTORY_PATH          | CORE                  | Path to the directory where to store logs in the container              |
| HOST_LOG_DIRECTORY_PATH     | CORE                  | Path to the directory where the logs are stored on the host system.     |
| LOG_LEVEL                   | CORE                  | Level of the log system. Can be INFO / WARNING / ERROR / DEBUG          |
| SPADE_PORT                  | CORE                  | Port where the API of erebot is listening                               |
