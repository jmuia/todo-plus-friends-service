# Welcome to your AppEngine starter kit

### Setup

[Install Python SDK for Google AppEngine](https://developers.google.com/appengine/downloads)

### Run debug server

```sh
make debug
# your debug server is now running at localhost:8080
```

### API.js

API.js is a tiny JavaScript interface for making API calls convenient.

Simply include it in your webapp and you will be able to make API calls to this service:

```html
<script src="http://localhost:8080/api.js"></script>
```

To make an API call in your JavaScript:

```js
API('POST', 'api/example', { json: 'data' },
    function (response, status) {
        // "response" is JSON output from the service
        // "status" is the HTTP status code returned by the API call
    }
);
```
