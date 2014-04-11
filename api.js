/*
	Usage (check out api/example.py):

	API('post', 'example', { value: 'foobar' }, function (data) {
		if (data.example_id) {
			API('get', 'example/'+data.example_id, function (example) {
				console.log(example.value);
			});
		}
	});

	To target a specific service URL:
	API.prefix = 'https://someotherservice.com/';
*/

var API = function () {
	var TIMEOUT = 25 * 1000;
	makeAPICall.prefix = 'https://myservice.appspot.com/';
	return makeAPICall;

	function makeAPICall (method, resource, data, callback) {
		if (typeof data === 'function') {
			callback = data;
			data     = null;
		}

		var done = false,
			xhr  = new XMLHttpRequest(),
			url  = makeAPICall.prefix + resource,
			contentType;
		method = method.toUpperCase();

		switch (method) {
			case 'POST':
			case 'PUT':
			case 'PATCH':
				if (data && (typeof data === 'object')) {
					contentType = 'application/json';
					data = JSON.stringify(data);
				} else {
					contentType = 'text/plain';
				}
				break;
			default:
				if (data && (typeof data === 'object')) {
					data = Object.keys(data).map(function (key) {
						return encodeURIComponent(key)+'='+encodeURIComponent(data[key]);
					}).join('&');
				}
				if (data) {
					var index = url.indexOf('?'),
						last  = url[url.length-1];
					if (index === -1) {
						url += '?';
					} else if (last !== '?' && last !== '&') {
						url += '&';
					}
					url += data;
					data = null;
				}
				break;
		}

		xhr.onreadystatechange = function () {
			if (xhr.readyState === 4) {
				xhrComplete(xhr.status);
			}
		};
		xhr.onload = function () {
			xhrComplete(xhr.status);
		};
		xhr.onerror = function () {
			xhrComplete(xhr.status);
		};

		xhr.timeout = TIMEOUT;
		xhr.ontimeout = function () {
			xhrComplete(0);
		};

		setTimeout(function () {
			if ( !done ) {
				xhr.abort();
				xhrComplete(0);
			}
		}, TIMEOUT);

		xhr.open(method, url, true);
		if (contentType) {
			xhr.setRequestHeader('Content-Type', contentType);
		}
		xhr.send(data);

		function xhrComplete (status) {
			if (done) {
				return;
			}
			done = true;

			var response;
			try {
				response = JSON.parse(xhr.responseText);
			} catch (err) {}

			if (callback) {
				callback(response, status);
			}
		}
	}
}();
