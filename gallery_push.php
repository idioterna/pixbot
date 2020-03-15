<?php

$date = intval($_POST['date']); // we only accept integers
$url = $_POST['url'];

if (empty($url) || $date < 1) die();

$filename = $date . ".jpg";

file_put_contents($filename, file_get_contents($url));

// optionally create a thumbnail
// system("convert $filename -thumbnail x200 -resize '200x<' -resize 50% -gravity center -crop 100x100+0+0 +repage -format jpg -quality 91 ./thumb/$filename");

?>
