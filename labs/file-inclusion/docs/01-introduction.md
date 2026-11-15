# Introduction

File inclusion happens when a web application reads a file based on user-supplied input without restricting which files can be accessed. The user controls all or part of the path, and the application does nothing to stop them from escaping the intended directory.

This lab simulates a site that serves static pages through a `page` query parameter. The application joins the parameter value with a base directory and opens the resulting path. Because it never strips `../` sequences, an attacker can climb out of the pages directory and read any file the process can open, including `/flag.txt`.

Local File Inclusion (LFI) is one of the most common vulnerabilities in PHP applications but appears in every language that builds file paths from user input.
