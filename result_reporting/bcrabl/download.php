
<?php
if(!session_id()) session_start();
$name = $_SESSION["name"];
$outfile = "/home/scratch/bcrabl/$name.out.csv";

if (file_exists($outfile)) {
    header('Content-Description: File Transfer');
    header('Content-Type: application/octet-stream');
    header('Content-Disposition: attachment; filename='.basename($outfile));
    header('Expires: 0');
    header('Cache-Control: must-revalidate');
    header('Pragma: public');
    header('Content-Length: ' . filesize($outfile));
    readfile($outfile);
exit;}

?>
