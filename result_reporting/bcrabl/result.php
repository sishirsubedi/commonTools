<html lang="en">
    <head>
        <title>BCR-ABL Reporting Interface </title>
        <link rel="stylesheet" href="form.css" >
    </head>
    <body >
<?php

if (empty($_FILES["sample_file"]['name'])){

  $message = 'Required file(s) not found.\\nTry again.';

  echo "<script type='text/javascript'>alert('$message');</script>";

  echo  "<script type='text/javascript'> window.location.href = 'http://10.110.21.70/bcrabl' </script>";

}

if(!session_id()) session_start();
session_unset();

##get the user input##
if (isset($_FILES["sample_file"]["name"])){

$name_withext = $_FILES["sample_file"]["name"];
$name = preg_replace('/\\.[^.\\s]{3,4}$/', '', $name_withext);
$_SESSION["name"] = $name;
$tmp_name = $_FILES['sample_file']['tmp_name'];
$error = $_FILES['sample_file']['error'];
$uploaddir = '/home/scratch/bcrabl/';
$uploadfile = $uploaddir . basename($_FILES['sample_file']['name']);
move_uploaded_file($tmp_name, $uploadfile );



##filter  result##
ob_implicit_flush(true);ob_end_flush();
$cmd = "python /var/www/html/bcrabl/filterBCRABL.py -i /home/scratch/bcrabl/$name.csv -o /home/scratch/bcrabl/$name.out.csv";
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

}
else {
          echo 'please choose a file';
          }
?>

<div class="container">
    <div id="form-main">
        <div id="form-div">
            <form class="montform" enctype="multipart/form-data" action="result.php" method="post">
              <a href='http://10.110.21.70/bcrabl' style="font-size: 30px;color:black;text-decoration:none">BCR-ABL Reporting Interface </a>
              <br></br>
              BCR-ABL output file is ready for download.
              <br></br>
              <br></br>
              <div class="submit">
                      <input type="button" class="button-blue" value="Download" onclick="window.location.href='download.php'" />
              </div>
            </form>
        </div>
    </div>
</div>
