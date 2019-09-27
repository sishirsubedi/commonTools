<head>
    <meta charset="utf-8">
    <title>HMVV3 Bug Reporting Tool</title>
    <link rel="stylesheet" href="form.css" >
</head>
<body style="background-color:grey;">
<?php
date_default_timezone_set('GMT');
session_start();

$credentials = explode("\n", file_get_contents('config.ini'));
$HMVVHOME_line=explode("=", $credentials[0]);
$HMVVHOME=$HMVVHOME_line[1];
$HOST_line=explode("=", $credentials[1]);
$HOST=$HOST_line[1];
$DATABASE_line=explode("=", $credentials[2]);
$DATABASE=$DATABASE_line[1];
$USER_line=explode("=", $credentials[3]);
$USER=$USER_line[1];
$PASS_line=explode("=", $credentials[4]);
$PASS=$PASS_line[1];

$connect = mysqli_connect("$HOST", "$USER", "$PASS", "$DATABASE");
$message = $_POST['message'];


if (empty($message)){

  $message = 'Description is empty';
  echo "<script type='text/javascript'>alert('$message');</script>";
  echo  "<script type='text/javascript'> window.location.href = '$HMVVHOME' </script>";

}

if (isset($_FILES["bug_image"]["name"])){

$filename_tl = $_FILES["bug_image"]["name"];
$filename_tl_tmp_name = $_FILES['bug_image']['tmp_name'];
$filename_tl_error = $_FILES['bug_image']['error'];
$filename_tl_ext = explode('.', $filename_tl);
$filename_tl_ext = strtolower(end($filename_tl_ext));
$location = '/var/www/html/hmvv3/images/';

$date = date_create();
$filename_date = date_timestamp_get($date);
$newfilename = $filename_date. '.' .$filename_tl_ext;
move_uploaded_file($filename_tl_tmp_name, $location.$newfilename);

$tl_allowed = array('png','jpg',);

// if(in_array($filename_tl_ext,$tl_allowed)){

  // if ($filename_tl_error === 0){

    $file = $filename_date. '.' .$filename_tl_ext;
    $query = "INSERT INTO hmvv3_bugs(message,bugURL) VALUES ('$message','$file')";
    if(mysqli_query($connect, $query))
    {
        echo '<script>alert("Feedback/Bug has been reported. Thank you !")</script>';
        echo  "<script type='text/javascript'> window.location.href = '$HMVVHOME' </script>";

        $message .= "\n\n\n Check Bug Report: http://10.110.21.70/hmvv34/bugsreport.php";
        // $to = "ssubedi@houstonmethodist.org,PAChristensen@houstonmethodist.org";
        $to = "ssubedi@houstonmethodist.org";
        mail($to,"HMVV3 Feedback/Bug Reported",$message);

    }
  // }
// }
ob_implicit_flush(true);
ob_end_flush();
}
?>
