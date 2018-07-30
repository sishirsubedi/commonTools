
<body style="background-color:powderblue;">

<p style="font-size:50px;">Iohexol Reporting Interface</p>

<?php
date_default_timezone_set('GMT');

session_start();

if (empty($_FILES["tasklist"]['name']) or empty($_FILES["tracefinder"]['name'])){



  $message = 'Files not uploaded.\\nTry again.';

  echo "<script type='text/javascript'>alert('$message');</script>";

  echo  "<script type='text/javascript'> window.location.href = 'http://10.110.21.70/iohexol/submit.html' </script>";

}

##get the user input##
else if (isset($_FILES["tasklist"]['name']) and isset($_FILES["tracefinder"]['name'])){

$filename_tl = $_FILES["tasklist"]["name"];
$filename_tl_tmp_name = $_FILES['tasklist']['tmp_name'];
$filename_tl_error = $_FILES['tasklist']['error'];
$filename_tl_ext = explode('.', $filename_tl);
$filename_tl_ext = strtolower(end($filename_tl_ext));

$tl_allowed = array('txt');

if(in_array($filename_tl_ext,$tl_allowed)){

  if ($filename_tl_error === 0){
    $location = '/home/scratch/iohexol/tasklist/';
    move_uploaded_file($filename_tl_tmp_name, $location.$filename_tl);
  }

}

$filename_tf = $_FILES["tracefinder"]["name"];
$filename_tf_tmp_name = $_FILES['tracefinder']['tmp_name'];
$filename_tf_error = $_FILES['tracefinder']['error'];
$filename_tf_ext = explode('.', $filename_tf);
$filename_tf_ext = strtolower(end($filename_tf_ext));

$tf_allowed = array('csv');

if(in_array($filename_tf_ext,$tf_allowed)){

  if ($filename_tf_error === 0){
    $location = '/home/scratch/iohexol/tracefinder/';
    move_uploaded_file($filename_tf_tmp_name, $location.$filename_tf);
  }
 }

$date = explode('_',$filename_tl);
$date = $date[2];
$date = explode('.',$date);
$date = $date[0];

$_SESSION['myvar'] = $date;

ob_implicit_flush(true);ob_end_flush();


$cmd = "/home/hhadmin/python3/bin/python3  iohex_reporting.py $date ";

$descriptorspec = array(
			0 => array("pipe", "r"),   // stdin is a pipe that the child will read from
			1 => array("pipe", "w"),   // stdout is a pipe that the child will write to
			2 => array("pipe", "w")    // stderr is a pipe that the child will write to
			);
flush();
$process = proc_open($cmd, $descriptorspec, $pipes, realpath('./'), array());
echo "<pre>";
if (is_resource($process)) {
  while ($s = fgets($pipes[1])) {
    print $s;
    flush();
  }
  while ($e = fgets($pipes[2])){
    print $e;
    flush();
  }
}
echo "</pre>";
proc_close($process);

} else {
  echo " file error. Download not available ";
}

?>
Click the link to download the  <mark>csv report </mark> results. <a href="download_report.php">Download!</a>
<br>
<br>
Click the link below to download the  <mark>pdf report </mark> results. <a href="download_pdf.php">Download!</a>
