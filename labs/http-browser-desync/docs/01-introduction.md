# Introduction

HTTP request smuggling happens when a frontend proxy and a backend server disagree on where one HTTP request ends and the next begins.

Both HTTP/1.1 mechanisms for specifying body length are legitimate: `Content-Length` (an exact byte count) and `Transfer-Encoding: chunked` (a streaming format with a terminator). When both headers appear in the same request, RFC 7230 says `Transfer-Encoding` takes precedence and `Content-Length` must be ignored. Not all servers follow this rule.

The CL.TE variant: the frontend uses `Content-Length`, the backend uses `Transfer-Encoding`. The frontend reads CL bytes and forwards them as the body. The backend parses the chunked body and stops at the terminator. Any bytes that the frontend sent as "body" but that come after the chunked terminator are treated by the backend as the start of a new HTTP request.

An attacker controls what goes in those trailing bytes. Putting `GET /admin` there makes the backend process an unauthorized admin request on the attacker's behalf.
