function showNotification(text, time = 3) {

    try {
        document.getElementById("notificationBox").remove();
    }
    catch {

    }
    // Create a container for the notification
    var notification = document.createElement('div');
    notification.style.position = 'fixed';
    notification.style.bottom = '20px';
    notification.style.right = '20px';
    notification.style.width = '400px';//'400px'; // Set width to 300 pixels
    notification.style.height = 'auto';//'200px'; // Set height to 100 pixels
    notification.style.backgroundColor = 'rgb(34,34,34)'; // Default background color
    notification.style.color = '#fff';
    notification.style.padding = '10px';
    notification.style.borderRadius = '10px'; // Rounded corners
    notification.style.border = '3px solid rgb(52, 53, 65)'; // 3px border with color
    notification.style.display = 'flex';
    notification.style.flexDirection = 'column-reverse'; // Stack notifications from bottom up
    notification.id = "notificationBox";


    // Add the required notification text
    var notificationText = document.createElement('div');
    notificationText.style.flex = '1'; // Make text flex to fit within the box
    notificationText.innerText = text;
    notificationText.style.fontSize = '30px';

    // Create a progress bar container
    var progressBarContainer = document.createElement('div');
    progressBarContainer.style.height = '10px';
    progressBarContainer.style.backgroundColor = 'transparent';
    progressBarContainer.style.marginTop = '5px'; // Add margin between text and progress bar

    // Create a progress bar
    var progressBar = document.createElement('div');
    progressBar.style.width = '100%';
    progressBar.style.height = '100%';
    progressBar.style.backgroundColor = '#007bff';

    // Add the progress bar to its container
    progressBarContainer.appendChild(progressBar);
    // Add the progress bar container and text to the notification
    notification.appendChild(notificationText);

    notification.appendChild(progressBarContainer);

    // Append the notification to the document
    document.body.appendChild(notification);

    // Animate the progress bar
    var startTime = Date.now();
    var duration = time * 1000; // Convert time to milliseconds
    function animateProgressBar() {
        var currentTime = Date.now();
        var elapsedTime = currentTime - startTime;
        var progress = (elapsedTime / duration) * 100;
        progressBar.style.width = 100 - progress + '%';
        if (progress < 100) {
            requestAnimationFrame(animateProgressBar);
        } else {
            // Remove the notification when the progress is complete
            document.body.removeChild(notification);
        }
    }

    // Start the animation only if a positive time is provided
    if (time > 0) {
        animateProgressBar();
    }
}

function httpGet(url, headers) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('GET', url);

        // Add headers to the request, if provided
        if (headers) {
            for (const header in headers) {
                xhr.setRequestHeader(header, headers[header]);
            }
        }

        xhr.onload = function () {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(xhr.responseText);
            } else {
                reject(new Error(`HTTP error ${xhr.status}: ${xhr.statusText}`));
            }
        };

        xhr.onerror = function () {
            reject(new Error('Network error'));
        };

        xhr.send();
    });
}
function httpPatch(url, headers = {}) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('PATCH', url);

        // Add headers to the request, if provided
        if (headers) {
            for (const header in headers) {
                xhr.setRequestHeader(header, headers[header]);
            }
        }

        xhr.onload = function () {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(xhr.responseText);
            } else {
                reject(new Error(`HTTP error ${xhr.status}: ${xhr.statusText}`));
            }
        };

        xhr.onerror = function () {
            reject(new Error('Network error'));
        };

        xhr.send();
    });
}
function httpDelete(url, headers = {}) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('DELETE', url);

        // Add headers to the request, if provided
        if (headers) {
            for (const header in headers) {
                xhr.setRequestHeader(header, headers[header]);
            }
        }

        xhr.onload = function () {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(xhr.responseText);
            } else {
                reject(new Error(`HTTP error ${xhr.status}: ${xhr.statusText}`));
            }
        };

        xhr.onerror = function () {
            reject(new Error('Network error'));
        };

        xhr.send();
    });
}
function httpPost(url, data = {}, headers = {}) {
    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();
        xhr.open('POST', url);

        // Add headers to the request
        for (const header in headers) {
            xhr.setRequestHeader(header, headers[header]);
        }
        let jsonData = '';
        try {
            // Convert the data object to a JSON string and set the content type header
            xhr.setRequestHeader('Content-Type', 'application/json');
            jsonData = JSON.stringify(data);
        } catch {
            xhr.setRequestHeader('Content-Type', 'application/octet-stream');
            jsonData = data;
        }

        xhr.onload = function () {
            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(xhr.responseText);
            } else {
                reject(new Error(`HTTP error ${xhr.status}: ${xhr.statusText}`));
            }
        };

        xhr.onerror = function () {
            reject(new Error('Network error'));
        };

        xhr.send(jsonData);
    });
}



showNotification("Welcome to the webui!")


    //< input type = "radio" name = "effect" checked = "true" id = "bw" />

    //<input type="radio" name="effect" id="gray" />

    //<input type="radio" name="effect" id="rainbow" />

    //<input type="radio" name="effect" id="inverted" />

    //<input type="radio" name="effect" id="blur" />

    //<input type="checkbox" id="erosion" checked="true" />

    //<input type="text" id="toptext" value="CP = Get reported to local police" />

    //<input type="text" id="secondtext" value="(Skipping will make it much worse if you stream CP :) )" />


function save() {

    config = {};
    if (document.getElementById("bw").checked) {
        config.mode = 1;
    }
    if (document.getElementById("invbw").checked) {
        config.mode = 6;
    }
    if (document.getElementById("gray").checked) {
        config.mode = 2;
    }
    if (document.getElementById("rainbow").checked) {
        config.mode = 3;
    }
    if (document.getElementById("inverted").checked) {
        config.mode = 4;
    }
    if (document.getElementById("blur").checked) {
        config.mode = 5;
    }
    if (document.getElementById("edges").checked) {
        config.mode = 7;
    }
    if (document.getElementById("rainbow_edges").checked) {
        config.mode = 7;
    }
    if (document.getElementById("none").checked) {
        config.mode = 0;
    }

    config.erosion = document.getElementById("erosion").checked;
    config.removebackground = document.getElementById("removebg").checked;

    config.toptext = document.getElementById("toptext").value;
    config.secondtext = document.getElementById("secondtext").value;

    config.width = document.getElementById("width").value;
    config.height = document.getElementById("height").value;

    config.useipserver = document.getElementById("useipserver").checked;
    config.trackhands = document.getElementById("usehands").checked;

    httpPost('/applysettings', config)
        .then(text => {
            showNotification("Ok");
        })
        .catch(error => {
            showNotification(`${error}`);
            console.error(error);
        });
}