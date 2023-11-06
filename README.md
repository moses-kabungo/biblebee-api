# BiblebeeApi

An ethuthiastic API for the bible app clients. [https://biblebee-api-035c43b7cf89.herokuapp.com/docs#/](Find it)

## Deployment

### Requirements
 - Docker and docker compose (Deploy on Infrastructure e.g., AWS)
 - Heroku account (PaaS option)
 - Firebase cloud message

By default, the API is deployable through docker (IaaS) or Heroku (PaaS). But you can virtually deploy to other platforms with minimal efforts.

### Environments
|Environment Variable|Description|
|--------------------|-----------|
|CELERY_BROKER_URL|Url to the messaging queue broker e.g., redis|
|CELERY_RESULT_BACKEND|Url to the backend results e.g., redis|
|FIREBASE_CONFIG_FILE|Path to the firebase config file|

### Docker

The compose file in the root of this project list down all the necessary components
