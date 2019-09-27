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
$CREATEACCOUNT_line=explode("=", $credentials[5]);
$CREATEACCOUNT=$CREATEACCOUNT_line[1];

$connect = mysqli_connect("$HOST", "$USER", "$PASS", "$DATABASE");

$ACCESSCODES = array("hmvv001", "hmvv012", "hmvv111");


$fullname = $_POST['fullname'];
$networkid = $_POST['networkid'];
$email = $_POST['email'];
$accesscode = $_POST['accesscode'];

if (  empty($fullname)  ||  empty($networkid) || empty($email) || empty($accesscode)  || !(isset($_POST['usertype'])) )
{
  $message = 'One or more fields empty';
  echo "<script type='text/javascript'>alert('$message');</script>";
  echo  "<script type='text/javascript'> window.location.href = '$HMVVHOME' </script>";

} else {

    $usertype = $_POST['usertype'];

    if( ! in_array($accesscode, $ACCESSCODES))
    {
      $message = 'Access code is incorrect. Try again.';
      echo "<script type='text/javascript'>alert('$message');</script>";
      echo  "<script type='text/javascript'> window.location.href = '$HMVVHOME' </script>";

    } else{

      $check_query="select networkID from user where networkID='$networkid'";

      $result = mysqli_query($connect, $check_query) or die(mysqli_error($connect));

      if( mysqli_num_rows($result) > 0)
      {
        $message = 'User exists in the system. Please make sure your network ID is correct.';
        echo "<script type='text/javascript'>alert('$message');</script>";
        echo  "<script type='text/javascript'> window.location.href = '$HMVVHOME' </script>";

      } else {

      // ob_implicit_flush(true);ob_end_flush();
      // $cmd = "sudo /bin/bash $CREATEACCOUNT  $networkid  >> /home/scratch/new_account.log";
      // $descriptorspec = array(
      // 			0 => array("pipe", "r"),   // stdin is a pipe that the child will read from
      // 			1 => array("pipe", "w"),   // stdout is a pipe that the child will write to
      // 			2 => array("pipe", "w")    // stderr is a pipe that the child will write to
      // 				);
      // 	flush();
      //
      // $process = proc_open($cmd, $descriptorspec, $pipes, realpath('./'), array());
      //
      // echo "<pre>";
      // if (is_resource($process)) {
      // 	while ($s = fgets($pipes[1])) {
      // 		print $s;
      // 		flush();
      //     }
      // 	while ($e = fgets($pipes[2])){
      // 		print $e;
      // 		flush();
      // 	}
      // 	}
      // echo "</pre>";
      // proc_close($process);

      $insert_query = "insert into user (networkID, userName, email, userType,accountType,status) values('$networkid','$fullname','$email','$usertype','$accesscode','active')";
      if(mysqli_query($connect, $insert_query))
      {
              echo '<script>alert("User has been registered. Thank you !")</script>';
              echo  "<script type='text/javascript'> window.location.href = '$HMVVHOME' </script>";

              $message .= "
              Thank you for your interest in Houston Methodist Variant Viewer application. A user account has been created for you.

              Username:  $networkid

              Password: (same as your network ID)
              ________________________________________
              Following is the link to download the application.

              $HMVVHOME
              ________________________________________
              This application requires a Java Runtime Environment. If your system does not have a Java installed, please contact IT-HELP DESK.


              Bioinformatics Team

              Molecular Diagnostics Lab Houston Methodist

              ";

              $from_add = "noreply@hmvv.houstonmethodist.org";

              $headers = "From: $from_add \r\n";
              $headers .= "Reply-To: $from_add \r\n";
              $headers .= "Return-Path: $from_add\r\n";
              $headers .= "X-Mailer: PHP \r\n";


              mail($email,"Houston Methodist Variant Viewer (HMVV) Account Confirmation",$message,$headers);
      }
    }
  }
}

?>
