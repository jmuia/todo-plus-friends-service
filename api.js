var MyService = function () {
	var API_URL = 'https://myservice.appspot.com/',
		TIMEOUT = 25 * 1000;

	return makeAPICall;

	function makeAPICall (resource, data, callback) {
		if (typeof data === 'function') {
			callback = data;
			data     = undefined;
		}

		var done = false,
			xhr  = new XMLHttpRequest(),
			url  = API_URL + resource;

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

		xhr.open('POST', url, true);
		xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8');
		xhr.send( JSON.stringify(data || {}) );

		function xhrComplete (status) {
			if (done) {
				return;
			}
			done = true;

			var response;
			if (status === 200) {
				try {
					response = JSON.parse(xhr.responseText);
				} catch (err) {}
			}

			if (callback) {
				callback((status === 0), response);
			}
		}
	}
}();
