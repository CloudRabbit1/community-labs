<?php
// Generate flags once at startup, read from files
$flag1 = trim(file_get_contents('/flag1.txt'));
$flag2 = trim(file_get_contents('/flag2.txt'));

// Simple session store
session_start();

// User database
$USERS = [
    'alice' => ['password' => 'alice123', 'role' => 'user'],
    'admin' => ['password' => null, 'role' => 'admin'],  // no login for admin
];

// ----------------------------------------------------------------
// Magic method gadget classes (simulating a "framework" in the app)
// ----------------------------------------------------------------

class Logger {
    public $logfile;
    public $message;

    // __destruct runs when the object is garbage-collected after unserialize()
    public function __destruct() {
        if ($this->logfile && $this->message) {
            file_put_contents($this->logfile, $this->message . "\n", FILE_APPEND);
        }
    }
}

class Template {
    public $tpl_file;

    // __toString called when object is used as a string
    public function __toString() {
        if ($this->tpl_file && file_exists($this->tpl_file)) {
            return file_get_contents($this->tpl_file);
        }
        return '';
    }
}

// ----------------------------------------------------------------
// Routing
// ----------------------------------------------------------------

$path = $_SERVER['REQUEST_URI'] ?? '/';
$path = strtok($path, '?');
$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';

function json_out($data, $code = 200) {
    http_response_code($code);
    header('Content-Type: application/json');
    echo json_encode($data);
    exit;
}

function get_body() {
    $raw = file_get_contents('php://input');
    return json_decode($raw, true) ?? [];
}

// GET / -- index
if ($path === '/' && $method === 'GET') {
    json_out([
        'app' => 'CorpCMS PHP Session API',
        'endpoints' => [
            'POST /login',
            'GET  /profile',
            'POST /session/save',
            'POST /session/restore',
            'GET  /admin/secret',
        ],
    ]);
}

// POST /login
if ($path === '/login' && $method === 'POST') {
    global $USERS;
    $body = get_body();
    $user = $body['username'] ?? '';
    $pass = $body['password'] ?? '';
    if (!isset($USERS[$user]) || $USERS[$user]['password'] !== $pass) {
        json_out(['error' => 'Invalid credentials'], 401);
    }
    $_SESSION['user'] = $user;
    $_SESSION['role'] = $USERS[$user]['role'];
    json_out(['message' => "Logged in as $user", 'role' => $USERS[$user]['role']]);
}

// GET /profile
if ($path === '/profile' && $method === 'GET') {
    global $flag1;
    if (empty($_SESSION['user'])) {
        json_out(['error' => 'Not authenticated'], 401);
    }
    $hint = ($_SESSION['role'] === 'admin') ? $flag1 : null;
    json_out(['username' => $_SESSION['user'], 'role' => $_SESSION['role'], 'hint' => $hint]);
}

// POST /session/save
if ($path === '/session/save' && $method === 'POST') {
    if (empty($_SESSION['user'])) {
        json_out(['error' => 'Not authenticated'], 401);
    }
    $data = ['user' => $_SESSION['user'], 'role' => $_SESSION['role']];
    $blob = base64_encode(serialize($data));
    json_out(['session_blob' => $blob, 'note' => 'POST to /session/restore to load']);
}

// POST /session/restore -- VULNERABLE
if ($path === '/session/restore' && $method === 'POST') {
    $body = get_body();
    $blob = $body['session_blob'] ?? '';
    if (!$blob) {
        json_out(['error' => 'session_blob required'], 400);
    }
    $raw = base64_decode($blob);
    // Bug: unserialize() on attacker-supplied data triggers magic methods
    $restored = unserialize($raw);
    if (!is_array($restored)) {
        json_out(['error' => 'Invalid session data'], 400);
    }
    $_SESSION['user'] = $restored['user'] ?? 'anonymous';
    $_SESSION['role'] = $restored['role'] ?? 'user';
    json_out(['message' => 'Session restored', 'user' => $_SESSION['user'], 'role' => $_SESSION['role']]);
}

// GET /admin/secret
if ($path === '/admin/secret' && $method === 'GET') {
    global $flag2;
    if (($_SESSION['role'] ?? '') !== 'admin') {
        json_out(['error' => 'Admin only'], 403);
    }
    json_out(['secret' => $flag2]);
}

// GET /debug/file?path=... (read arbitrary file -- simulates a separate __toString gadget chain result)
if ($path === '/debug/file' && $method === 'GET') {
    $f = $_GET['path'] ?? '';
    if ($f && file_exists($f)) {
        json_out(['content' => file_get_contents($f)]);
    }
    json_out(['error' => 'file not found'], 404);
}

json_out(['error' => 'Not found'], 404);
