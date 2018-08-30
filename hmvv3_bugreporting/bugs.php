<head>
    <meta charset="utf-8">
    <title>HMVV3 Bug Reporting Tool</title>
    <link rel="stylesheet" href="form.css" >
</head>
<body style="background-color:grey;">
<?php
date_default_timezone_set('GMT');
session_start();

$connect = mysqli_connect("localhost", "", "", "");

if (empty($_FILES["bug_image"]["name"])){

  $message = 'Image not uploaded.\\nTry again.';
  echo "<script type='text/javascript'>alert('$message');</script>";
  echo  "<script type='text/javascript'> window.location.href = 'http://10.110.21.70/hmvv3/bugs.html' </script>";

}

if (isset($_FILES["bug_image"]["name"])){

$filename_tl = $_FILES["bug_image"]["name"];
$filename_tl_tmp_name = $_FILES['bug_image']['tmp_name'];
$filename_tl_error = $_FILES['bug_image']['error'];
$filename_tl_ext = explode('.', $filename_tl);
$filename_tl_ext = strtolower(end($filename_tl_ext));

$tl_allowed = array('png','jpg',);

$message = $_POST['message'];

if(in_array($filename_tl_ext,$tl_allowed)){

  if ($filename_tl_error === 0){

    $file = addslashes(file_get_contents($filename_tl_tmp_name));
    $query = "INSERT INTO hmvv3_bugs(message,bugImage) VALUES ('$message','$file')";
    if(mysqli_query($connect, $query))
    {
        echo '<script>alert("Bug has been reported. Thank you !")</script>';
        echo  "<script type='text/javascript'> window.location.href = 'http://10.110.21.70/hmvv3/bugs.html' </script>";

        $message .= "\n\n\n Check Bug Report: http://10.110.21.70/hmvv3/bugsreport.php";
        // $to = "ssubedi@houstonmethodist.org,PAChristensen@houstonmethodist.org";
        $to = "ssubedi@houstonmethodist.org";
        mail($to,"HMVV3 Bug Reported",$message);

    }
  }
}
ob_implicit_flush(true);
ob_end_flush();
}
?>
