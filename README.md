# API Documentation

This document outlines the functionalities and endpoints provided by the fetchbytes.com API, including the parameters required and the response structure. The API uses a RESTful approach with the server implemented using Express.js.

## Table of Contents

1. [Quickstart Guide](#quickstart-guide)
1. [Configuration Endpoint](#configuration-endpoint)
2. [Navigation Endpoint](#navigation-endpoint)
3. [Interaction Endpoint](#interaction-endpoint)
4. [Data Extraction Endpoint](#data-extraction-endpoint)
5. [PDF Generation Endpoint](#pdf-generation-endpoint)
6. [Screenshot Endpoint](#screenshot-endpoint)

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


## Configuration Endpoint

### URL

`POST /configure`

### Description

Configures a new session with the given worker configuration settings. If the configuration is successful, it returns a session ID.

### Parameters

- `viewport` (string): Viewport size in the format `WIDTHxHEIGHT` (e.g., `1920x1080`).
- `proxyCountry` (string): Proxy country code or residential proxy settings.
- `userAgent` (string): Custom User-Agent string.
- `extraHTTPHeaders` (object): Extra HTTP headers to be used in the session.
- `enableAdBlock` (boolean): Whether to enable ad blocking (default is `true`).
- `blockResources` (boolean|array): Resources to block (e.g., `["image", "media"]`).
- `keepAlive` (integer): Keep-alive duration in seconds (default is `1`). How long session is kept alive after last request. If you don't make a new request within specified timeframe session is disposed.

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

#### Solve Captchas Action

Automatically solves captchas that are present on the page.

**Parameters:**

- `action` (string): Should be set to `"solveCaptchas"`.

**Example:**

```json
{
  "action": "solveCaptchas"
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
- `extract` (object): A map of key-value pairs specifying the data to be extracted.
- `content` (boolean): Whether to return the page content. Default is `false`.

### Response

#### Success

- `data` (object): The extracted data.
- `content` (string|null): The page content if requested.
- `url` (string): The current URL after data extraction.

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
- `fullPage` (boolean): Whether to capture the full page (default is `false`).

### Response

#### Success

- The content-type is set to `image/png` and the screenshot data is returned in the response.

#### Error

- `error` (string): Error message.

---

Please ensure to handle error cases accordingly by checking for the presence of an `error` field in the response which indicates what went wrong during the request.
