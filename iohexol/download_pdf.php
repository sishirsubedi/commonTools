
<?php
date_default_timezone_set('GMT');


session_start();

$date =$_SESSION['myvar'];

$outfile = "/home/scratch/iohexol/report/Iohexol_report_$date.pdf";

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
