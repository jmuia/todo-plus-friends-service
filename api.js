var API = function (kik) {
	var TIMEOUT   = 25 * 1000,
			TOKEN_KEY = '__KIK_SESSION__';

	// change the prefix to the host of your desire for testing
	makeAPICall.prefix = 'https://myservice.appspot.com';
	makeAPICall.auth = authenticatedAPICall
	return makeAPICall;


	function authenticatedAPICall(method, resource, data, callback) {
		if (typeof data === 'function') {
			callback = data;
			data     = null;
		}
		method = method.toUpperCase();

		if (!kik || !kik.sign) {
			if (callback) {
				callback(null, 0);
			}
			return;
		}

		var payload, asHeader;
		switch (method) {
			case 'POST':
			case 'PUT':
			case 'PATCH':
				if (data && (typeof data === 'object')) {
					payload = JSON.stringify(data);
				} else {
					payload = data;
				}
				data = null;
				asHeader = false;
				break;
			default:
				payload = resource.split('?')[0];
				asHeader = true;
				break;
		}

		kik.sign(payload, function (jws) {
			if ( !jws ) {
				callback(null, 0);
				return;
			}
			var headers = {};
			if (asHeader) {
				headers['X-Kik-JWS'] = jws;
			} else {
				data = jws;
			}
			makeAPICall(method, resource, data, callback, headers);
		});
	}

	function makeAPICall (method, resource, data, callback, headers) {
		if (typeof data === 'function') {
			headers  = callback;
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
		for (var key in headers) {
			xhr.setRequestHeader(key, headers[key]);
		}
		setSession(xhr);
		xhr.send(data);

		function xhrComplete (status) {
			if (done) {
				return;
			}
			done = true;

			storeSession(xhr);

			var response;
			try {
				response = JSON.parse(xhr.responseText);
			} catch (err) {}

			if (callback) {
				callback(response, status);
			}
		}
	}

	function setSession(xhr) {
		var sessionToken = localStorage[TOKEN_KEY];
		if (sessionToken) {
			xhr.setRequestHeader('X-Kik-User-Session', sessionToken);
		}
	}

	function storeSession(xhr) {
		try {
			var header       = xhr.getResponseHeader('Content-Type'),
					sessionToken = /\bkik\-session\=(\S+)\b/.exec(header)[1];
			if (sessionToken) {
				localStorage[TOKEN_KEY] = sessionToken;
			}
		} catch (err) {}
	}
}(window.kik);
