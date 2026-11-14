# Finding the Bug

## Spot the Sink

Open `http://localhost:8080/reflect?q=hello`. The page shows "hello" in the results div.

Now try `http://localhost:8080/reflect?q=<b>bold</b>`. If the word "bold" appears in bold, the HTML was parsed. That means your input went through `innerHTML`, not `textContent`.

View the page source. You will see:

```html
<div id="results"></div>
<script>
  document.getElementById('results').innerHTML = "hello";
</script>
```

The value is injected directly into the JavaScript string, which is then assigned to `innerHTML`. Anything you put in `q` ends up interpreted as HTML.

## Probe for Script Execution

Try: `http://localhost:8080/reflect?q=<img src=x onerror=alert(1)>`

In a real browser, this fires an alert. In the test harness, you verify that the raw payload appears unescaped in the HTML source.
