<?php
/**
 * Supreme Food Industry — PHP contact intake (Apache/Nginx PHP-FPM deploy)
 * Alternative to the Flask /api/contact endpoint.
 */
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['ok' => false, 'error' => 'POST only', 'lang' => 'php']);
    exit;
}

$raw = file_get_contents('php://input');
$data = json_decode($raw, true);
if (!is_array($data)) {
    $data = $_POST;
}

$name = trim($data['name'] ?? '');
$phone = preg_replace('/\D+/', '', $data['phone'] ?? '');
$message = trim($data['message'] ?? '');

if (mb_strlen($name) < 2) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'कृपया नाम लेख्नुहोस्।', 'lang' => 'php']);
    exit;
}
if (strlen($phone) < 10) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'मान्य मोबाइल नम्बर दिनुहोस्।', 'lang' => 'php']);
    exit;
}

$dir = __DIR__ . '/../../data';
if (!is_dir($dir)) {
    mkdir($dir, 0775, true);
}
$file = $dir . '/php_inquiries.jsonl';
$entry = [
    'name' => $name,
    'phone' => $phone,
    'message' => $message,
    'created_at' => gmdate('c'),
    'lang' => 'php',
];
file_put_contents($file, json_encode($entry, JSON_UNESCAPED_UNICODE) . PHP_EOL, FILE_APPEND);

echo json_encode([
    'ok' => true,
    'lang' => 'php',
    'message' => 'धन्यवाद — PHP बाट सन्देश सेभ भयो।',
    'company_mobiles' => ['9841043864', '9840067681'],
], JSON_UNESCAPED_UNICODE);
