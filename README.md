# API Documentation

This document outlines the functionalities and endpoints provided by the fetchbytes.com API, including the parameters required and the response structure. The API uses a RESTful approach with the server implemented using Express.js.

## Table of Contents

1. [Quickstart Guide](#quickstart-guide)
1. [Using the API](#using-the-api)
1. [Handling Errors](#handling-errors)
1. [Debugging](#debugging)
1. [Configuration Endpoint](#configuration-endpoint)
1. [Navigation Endpoint](#navigation-endpoint)
1. [Interaction Endpoint](#interaction-endpoint)
1. [Data Extraction Endpoint](#data-extraction-endpoint)
1. [PDF Generation Endpoint](#pdf-generation-endpoint)
1. [Screenshot Endpoint](#screenshot-endpoint)

---

# Quickstart Guide

This quickstart guide will demonstrate how to use the API to navigate to web pages, generate PDFs, take screenshots, and interact with web elements using cURL commands. In each example, replace `YOUR_API_KEY` with your actual API key.

All requests should be made to `https://api.fetchbytes.com/` webserver. Both snake_case and camelCase top level endpoint parameters are supported. For consistency in this documentation camelCase is used.

## Examples

### Navigating to a Web Page

To navigate to a web page and fetch its content:

```sh
$ curl "https://api.fetchbytes.com/navigate?key=YOUR_API_KEY&url=https://httpbin.org/anything&content=True"
```

**Example Response:**

```json
{
  "url": "https://httpbin.org/anything",
  "status": 200,
  "content": "<html><head><meta ...</div></body></html>",
  "actions": [],
  "data": {},
  "transfer_size": 1178,
  "session": "cwJyBV930X"
}
```

### Generating a PDF

To generate a PDF from a specific URL:

```sh
$ curl "https://api.fetchbytes.com/pdf?key=YOUR_API_KEY&url=https://example.com" > res.pdf
```

### Taking a Page Screenshot

To take a screenshot of a specific URL:

```sh
$ curl "https://api.fetchbytes.com/screenshot?key=YOUR_API_KEY&url=https://example.com" > res.png
```

### Navigating to a Web Page, Interacting and Extracting Data

To navigate to a web page, perform actions, and extract data:

```sh
$ curl -X POST "https://api.fetchbytes.com/navigate?key=YOUR_API_KEY" \
-H "Content-Type: application/json" \
-d '{
  "url": "https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)",
  "actions": [
    {
      "action": "click",
      "element": ".wikitable > thead:nth-child(2) > tr:nth-child(1) > th:nth-child(1)"
    }
  ],
  "extract": {
    "table": "table.wikitable"
  },
  "content": false
}'
```

By following these examples, you can quickly start using the API to automate web interactions, generate PDFs, take screenshots, and extract data efficiently.

## Using the API

This section outlines the foundational concepts needed for making requests to the FetchBytes API. This will be particularly useful for developers who are interfacing with the API for the first time.

### Basic Concepts

#### API Endpoint

All API requests should be directed to the following base URL:

```
https://api.fetchbytes.com/?key=YOUR_API_KEY
```

Make sure to replace `YOUR_API_KEY` with your actual API key in all requests.


#### Supported Request Methods

The FetchBytes API supports both `GET` and `POST` request methods depending on the type of operation being performed.

- **GET**: Used primarily for simple navigation, taking screenshots/PDFs.
- **POST**: Used for operations where you are sending data, for instance, when performing interactions or navigations on a web page.

### Authorization

To authenticate your requests, include your API key as a query parameter named `key`. You can also pass the API key as `api_key` URL parameter or in `X-Api-Key` HTTP Header.


Example of a `GET` request:

```sh
$ curl "https://api.fetchbytes.com/navigate?key=YOUR_API_KEY&url=https://httpbin.org/anything"
```

Example of a `POST` request:

```sh
$ curl -X POST "https://api.fetchbytes.com/navigate?key=YOUR_API_KEY" -H "Content-Type: application/json" -d '{...}'
```

### Request Headers

For POST requests, ensure that you set the correct `Content-Type` header to `application/json`.

```sh
-H "Content-Type: application/json"
```

### Response Structure

Most endpoints return JSON responses. A typical response includes fields such as:

- `url`: Current page URL after executing a reques.
- `session`: Browser session ID. Reuse same session id on subsequent requests to use the same browser.
- `error`: Error message, if there are any error (see Errors sections for more details).
- `transferSize`: Number of traffic used while processing your requests. Our billing is traffic based. Using this number you can better control your expenses.
- other fileds depend on the API request made.


## Handling Errors

There are two types of errors possible in the system:

1. **Errors produced by incorrect usage of the API**: When such an error occurs, the API returns an HTTP status code other than 200, and the JSON result contains only one field: `error`.

2. **Errors occurring during interaction with target websites**: These errors are not reflected in the API HTTP response status, which remains 200. However, the result contains an `error` key with an error message alongside other result data. The only exceptions are methods that return binary data (e.g., PDF, screenshot). In case of an error, they return an HTTP response code other than 200.

### HTTP Error Codes

| HTTP Status           | Status Code | Scenario                                                                           |
|-----------------------|-------------|------------------------------------------------------------------------------------|
| OK                    | 200         | Successful completion of commands                                                  |
| Bad Request           | 400         | API protocol error when a request is invalid or malformed                          |
| Payment Required      | 402         | You have reached your usage limit. Consult app dashboard for more information      |
| Conflict              | 409         | When error happened during browser interaction but JSON response can't be returned |
| Too Many Requests     | 429         | When you have used maximum number of concurrent sessions on your account           |
| Unprocessable Entity  | 422         | SessionError when a session is invalid or nonexistent                              |
| Internal Server Error | 500         | Any other unspecified errors                                                       |

These statuses cover different error types and other situations encountered during HTTP request handling.

## Debugging

Enabling session debugging can be useful while developing your code. When it is on, each result will have additional fields: `debugLog` — an array of debug messages and browser console logs, and `debugScreenshot` — a base64 ecoded png file with the current page screenshot.

Additionally, any executed action will contain a `debugScreenshot` of the current page after executing the action.

Example:

```json
{
   ...result fields...,
   "actions": [{
       "action": ...,
       "debugScreenshot": "base64"
   }],
   "debugScreenshot": "base64",
   "debugLog": ["string"]
}
```

## Session Configuration Endpoint

### URL

`POST /session`

### Description

Configures a new session with the given worker configuration settings. If the configuration is successful, it returns a session ID.

Also force session deletion for better concurrency management

### Parameters

- `viewport` (string): Viewport size in the format `WIDTHxHEIGHT` (e.g., `1920x1080`).
- `proxyCountry` (string): Proxy country code or residential proxy settings.
- `userAgent` (string): Custom User-Agent string.
- `extraHTTPHeaders` (object): Extra HTTP headers to be used in the session.
- `enableAdBlock` (boolean): Whether to enable ad blocking (default is `true`). (Temporary disabled)
- `blockResources` (boolean|array): Resources to block (e.g., `["image", "media"]`).
- `keepAlive` (integer): Keep-alive duration in seconds (default is `1`). How long session is kept alive after last request. If you don't make a new request within specified timeframe session is disposed.
- `debug` (boolean): Enable session debugging. Set to true to enable extended output.

Parameters to stop session:

- `session` (string): The session ID to stop.
- `stop` (boolean): Set to `true` to stop the session.


### Proxy Countries

You can use either datacenter-based or residential proxies. The following datacenter proxy regions are available to configure: "US", "ES", "DE", "NL", "FR", "UK", "SG", "AU", "CA", "IN" (corresponding to ISO 2-letter country codes). If you don't specify a proxy country, a random datacenter proxy is used.

To use a residential proxy, prefix the country code with `RS-`, e.g., `RS-US`, `RS-ES`, `RS-CA`. In addition, general Europe `RS-EU` and Asia regions `RS-RSA` are available. You can also use a random global residential proxy by specifying just the `RS` prefix without a country code.

### Response

#### Success

- `session` (string): The ID of the new session.

#### Error

- `error` (string): Error message.

---

## Navigation Endpoint

### URL

`POST /navigate`

### Description

Navigates to a specified URL and optionally performs actions and extracts content/data from the page.

### Parameters

- `session` (string): The session ID obtained from `/configure`.
- `url` (string): The URL to navigate to.
- `newContext` (boolean): Whether to create a new browser context (default is `true`).
- `content` (boolean): Whether to return the page content (default is `true`).
- `timeout` (integer): Navigation timeout in milliseconds (default is `30000`).
- `waitUntil` (string): When to consider navigation succeeded (e.g., `load`, `domcontentloaded`). Default is `load`.
- `actions` (array): A list of actions to perform on the page (See Interaction endpoint).
- `extract` (object): A map of key-value pairs specifying the data to extract from the page after all actions are completed sucessfully

### Response

#### Success

- `url` (string): The current URL after navigation.
- `status` (integer): HTTP status code of the response.
- `content` (string|null): The page content if requested.
- `actions` (array): The results of actions performed.
- `data` (object): The extracted data.

#### Error

- `error` (string): Error message.

---

## Interaction Endpoint

### URL

`POST /interact`

### Description

Performs a series of actions on the currently loaded page within the provided session.

### Parameters

- `session` (string): The session ID obtained from `/configure`.
- `actions` (array): A list of actions to perform on the page.

### Response

#### Success

- `actions` (array): The results of actions performed.
- `url` (string): The current URL after interactions.

#### Error

- `error` (string): Error message.

### Action Types

The `/interact` endpoint supports a variety of actions that can be performed on a page. These actions allow you to interact with elements on the page in different ways such as filling forms, clicking buttons, waiting for certain elements, and more.


1. **Fill Action**
2. **Click Action**
3. **Wait Action**
4. **Focus Action**
5. **Hover Action**
6. **Solve Captchas Action**
7. **Evaluate**

### Action Details

#### Fill Action

Fills a specified input field with the provided text.

**Parameters:**

- `action` (string): Should be set to `"fill"`.
- `element` (string): Selector of the element to fill.
- `value` (string): Text to fill into the element.
- `typingDelay` (integer, optional): Delay between key presses in milliseconds (default is `20`).
- `skipNavigation` (boolean, optional): Whether to skip waiting for navigation after the action (default is `false`).

**Example:**

```json
{
  "action": "fill",
  "element": "#username",
  "value": "myUsername",
  "typingDelay": 50,
  "skipNavigation": false
}
```

#### Click Action

Clicks a specified element on the page.

**Parameters:**

- `action` (string): Should be set to `"click"`.
- `element` (string): Selector of the element to click.
- `button` (string, optional): Mouse button to use for the click (`"left"`, `"right"`, `"middle"`) (default is `"left"`).
- `clickCount` (integer, optional): Number of times to click (default is `1`).
- `skipNavigation` (boolean, optional): Whether to skip waiting for navigation after the action (default is `false`).

**Example:**

```json
{
  "action": "click",
  "element": "#submit-button",
  "button": "left",
  "clickCount": 1,
  "skipNavigation": false
}
```

#### Wait Action

Waits for a specified element to appear on the page.

**Parameters:**

- `action` (string): Should be set to `"wait"`.
- `element` (string): Selector of the element to wait for.
- `value` (string, optional): Text to match within the element.
- `isRegex` (boolean, optional): Whether the text parameter should be treated as a regular expression (default is `false`).
- `invert` (boolean, optional): Whether to invert the waiting condition (i.e., wait for the element to not appear) (default is `false`).

**Example:**

```json
{
  "action": "wait",
  "element": "#message",
  "value": "Success",
  "isRegex": false,
  "invert": false
}
```

#### Focus Action

Moves focus to a specified element on the page.

**Parameters:**

- `action` (string): Should be set to `"focus"`.
- `element` (string): Selector of the element to focus on.

**Example:**

```json
{
  "action": "focus",
  "element": "#search-box"
}
```

#### Hover Action

Moves the mouse pointer over a specified element.

**Parameters:**

- `action` (string): Should be set to `"hover"`.
- `element` (string): Selector of the element to hover over.

**Example:**

```json
{
  "action": "hover",
  "element": "#dropdown-menu"
}
```

#### Solve Captcha Action

Solves captchas that are present on the page. We use third-party human-powered captcha solving as well as AI-based OCR solutions to solve captchas choosing the best option automatically.

**Parameters:**

- `action` (string): Should be set to `"solveCaptcha"`.
- `captchaType` ("recaptcha" | "image" | "turnstile" ): type of the captcha to solve
- `element` (string): element containing the captcha image to solve. Required in case of "image" captcha type.

*WARNING*: make sure to use large session timeout when solving captchas as it may take some time to solve them. Always use `configure` endpoint to set a large timeout before solving captchas.

For `recaptcha` (for all captchas that require solving a puzzle), and `turnstile` (cloudflare turnstile) captchas, the captcha is solved automatically. No need to pass any element.

When solving `image` captchas, the `element` parameter should be set to the selector of the image element containing the captcha only for captcha type other than "recaptcha" and "hcaptcha". For these types, the captcha is solved automatically.

**Example:**

```json
{
  "action": "solveCaptchas",
  "captchaType": "image",
  "element": "#captcha-image"
}
```

Response for "image" captcha:

```json
{
  "actions": [
    {
      "action": "solveCaptcha",
      "result": {'id': 'captchaId', 'solution': 'captchaSolution'},
      "selector": "#captcha-image",
      "verbose": "Captcha solved"
    }
  ]
}
```

You can use `solution` value to fill the captcha input field in subsequent actions.

Response `result` for "recaptcha" and "hcaptcha" will include:
- `captchas` is an array of captchas found in the page
- `filtered` is an array of captchas that have been detected but are ignored due to plugin options
- `solutions` is an array of solutions returned from the provider
- `solved` is an array of "solved" (= solution entered) captchas on the page

E.g.:
```
{ 'actions': [ { 'action': 'solveCaptcha',
                 'result': { 'captchas': [ { '_type': 'checkbox',
                                             '_vendor': 'recaptcha',
                                             'display': { 'height': 0,
                                                          'left': 825,
                                                          'size': None,
                                                          'theme': None,
                                                          'top': 280,
                                                          'width': 0},
                                             'hasResponseElement': True,
                                             'id': 'qxa....p30n',
                                             'isEnterprise': False,
                                             'isInViewport': True,
                                             'isInvisible': False,
                                             's': None,
                                             'sitekey': '6LfD3PI........3eXSqpPSRFJ_u',
                                             'url': 'https://somedomain.com/page',
                                             'widgetId': 0}],
                             'filtered': [],
                             'solutions': [ { '_vendor': 'recaptcha',
                                              'duration': 4.295,
                                              'hasSolution': True,
                                              'id': 'qxafdqr9p30n',
                                              'provider': '2captcha',
                                              'providerCaptchaId': '77181937438',
                                              'requestAt': '2024-08-18T17:25:25.493Z',
                                              'responseAt': '2024-08-18T17:25:29.788Z',
                                              'text': '03....ZKU'}],
                             'solved': [ { '_vendor': 'recaptcha',
                                           'id': 'q....9p30n',
                                           'isSolved': True,
                                           'responseCallback': False,
                                           'responseElement': True,
                                           'solvedAt': {}}]},
                 'verbose': 'Captcha solved'}],
}
```

In case of error solving captcha, the `result` will include `error` field with the error message.

#### Evaluate Action

Evaluates a JavaScript expression on the page.

**Parameters:**

- `action` (string): Should be set to `"click"`.
- `element` (string): Selector of the element to click.
- `button` (string, optional): Mouse button to use for the click (`"left"`, `"right"`, `"middle"`) (default is `"left"`).
- `clickCount` (integer, optional): Number of times to click (default is `1`).
- `skipNavigation` (boolean, optional): Whether to skip waiting for navigation after the action (default is `false`).

**Example:**

Request
```json
{
  "action": "evaluate",
  "value": "document.querySelector('h1').innerText",
}
```

Response:
```json
{
  "actions": [ {
    "action": "evaluate",
    "result": "Header Text",
    "selector": None,
    "verbose": "Script evaluated successfully"
    } ]
}
```


### Full Example

Here is an example of a full interaction request which uses a combination of different actions:

```json
{
  "session": "abcd1234",
  "actions": [
    {
      "action": "fill",
      "element": "#username",
      "value": "myUsername",
      "typingDelay": 50,
      "skipNavigation": false
    },
    {
      "action": "fill",
      "element": "#password",
      "value": "myPassword",
      "typingDelay": 50,
      "skipNavigation": false
    },
    {
      "action": "click",
      "element": "#login",
      "skipNavigation": false
    },
    {
      "action": "wait",
      "element": "#welcome-message",
      "value": "Welcome",
      "isRegex": false,
      "invert": false
    },
    {
      "action": "solveCaptchas"
    }
  ]
}
```

In this example, the following happens:

1. The username is filled into the `#username` field.
2. The password is filled into the `#password` field.
3. The login button (`#login`) is clicked.
4. The script waits for an element with `#welcome-message` containing the text "Welcome" to appear.
5. Any captchas present on the page are solved automatically.

By using a combination of these actions, you can interact with web pages in various ways and automate complex workflows.

---

## Data Extraction Endpoint

### URL

`POST /data`

### Description

Extracts specified data from the currently loaded page within the provided session.

### Parameters

- `session` (string): The session ID obtained from `/configure`.
- `extract` (Map<key:selector>): A map of key-value pairs specifying the data to be extracted. See selector specification below.
- `content` (boolean): Whether to return the page content. Default is `false`.

### Accepted Selectors and Their Processing:

#### 1. Valid CSS Selectors
CSS selectors, including complex ones with spaces, `#`, `(`, `=`, or `*`, are directly processed using `document.querySelector`.

**Example:**
```javascript
document.querySelector("div.className")
```

#### 2. Element ID
Element IDs are checked by attempting to retrieve the element using `document.getElementById`. This method is used if the `selector` does not contain any `[` character.

**Example:**
```javascript
document.getElementById("myElementId")
```

#### 3. Element Name
Element names are processed using `document.getElementsByName`. This method is used if an element ID or complex CSS selector match is not found.

**Example:**
```javascript
document.getElementsByName("myElementName")
```

#### 4. Valid XPath
XPath selectors start with a `/` and are processed using `document.evaluate`. XPath searches are used to locate elements that may not be easily targeted with CSS selectors or IDs.

**Example:**
```javascript
document.evaluate("/html/body/div[1]", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue
```

#### 5. Shadow DOM Selectors
Shadow DOM selectors are checked if the `selector` contains `#shadow-root`. These selectors are split and queried sequentially within each shadow root.

**Example:**
```javascript
let parts = selector.split('#shadow-root');
element = document.querySelector(parts[0]);
for (let i = 1; i < parts.length && element != null; i++) {
    element = element.shadowRoot;
    element = element.querySelector(parts[i]);
}
```

### Response

#### Success

- `data` (Map<key:Array<Extracted Data>): The extracted data as key-value pairs corresponding to `extract` parameter. Each value is a an array of data elements if multiple elements on page match selector
- `content` (string|null): The page content if requested.
- `url` (string): The current URL after data extraction.

###  Extracted Data Structure
The returned data object contains the following properties:

- `tag` (string): The tag name of the element.
- `value` (string | null): The value associated with the element (e.g., `href` for links, `value` for inputs).
- `text` (string | null): The text content of the element.
- `options` (Array<{ value: string, text: string }> | null): An array of option objects for `<select>` elements.
- `html` (string): The outer HTML of the element.
- `rows` (Array<Array<string>> | null): The rows of a `<table>` element.
- `headers` (Array<Array<string>> | null): The headers of a `<table>` element.

### Target Elements and Respective Data

#### `<a>` (Anchor Element)
- `tag`: "a"
- `value`: URL (string)
- `text`: null
- `options`: null
- `html`: Outer HTML (string)
- `rows`: null
- `headers`: null

#### `<input>` and `<textarea>` (Input/Textarea Elements)
- `tag`: "input" / "textarea"
- `value`: Input value (string)
- `text`: null
- `options`: null
- `html`: Outer HTML (string)
- `rows`: null
- `headers`: null

#### `<select>` (Select Element)
- `tag`: "select"
- `value`: Selected option value (string)
- `text`: Selected option text (string)
- `options`: Array of options (each with `value` and `text`)
- `html`: Outer HTML (string)
- `rows`: null
- `headers`: null

#### `<table>` (Table Element)
- `tag`: "table"
- `value`: null
- `text`: null
- `options`: null
- `html`: Outer HTML (string)
- `rows`: Array of rows (each row is an array of cell content)
- `headers`: Array of headers (each header is an array of cell content)

#### Other Elements (Fallback)
- `tag`: Corresponding tag name
- `value`: null
- `text`: Text content (string)
- `options`: null
- `html`: Outer HTML (string)
- `rows`: null
- `headers`: null

## Example
```json
[
  {
    tag: "a",
    value: "https://example.com",
    text: null,
    options: null,
    html: '<a href="https://example.com" class="some-link-class">Link Text</a>',
    rows: null,
    headers: null
  }
  // ...more items if multiple elements match
]
```


#### Error

- `error` (string): Error message.

---

## PDF Generation Endpoint

### URL

`POST /pdf`


### Description

Generates a PDF of the specified URL or the currently loaded page within the provided session.

### Parameters

- `session` (string): The session ID obtained from `/configure`.
- `url` (string): The URL of the page to generate the PDF from (optional if `session` is specified).

### Response

#### Success

- The content-type is set to `application/pdf` and the PDF data is returned in the response.

#### Error

- `error` (string): Error message.

---

## Screenshot Endpoint

### URL

`POST /screenshot`

### Description

Captures a screenshot of the specified URL or the currently loaded page within the provided session.

### Parameters

- `session` (string): The session ID obtained from `/configure`.
- `url` (string): The URL of the page to capture the screenshot from (optional if `session` is specified).
- `element` (string): selector of an element to take screenshot of. If passed only this element is captured.
- `fullPage` (boolean): Whether to capture the full page (default is `false`) or current viewport.

### Response

#### Success

- The content-type is set to `image/png` and the screenshot data is returned in the response.

#### Error

- `error` (string): Error message.

---

Please ensure to handle error cases accordingly by checking for the presence of an `error` field in the response which indicates what went wrong during the request.
