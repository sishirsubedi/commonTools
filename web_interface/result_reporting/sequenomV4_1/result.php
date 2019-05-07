<html lang="en">
    <head>
        <title>SequenomV4 Home</title>
        <link rel="stylesheet" href="form.css" >
    </head>

    <body >

<?php

if (isset($_POST['assay']))
  {
    $radioVal = $_POST["assay"];

    if($radioVal == "Oncocarta")  {
        // echo("You chose the Oncocarta Assay.");


        if (empty($_FILES["mutation_file"]['name']) or empty($_FILES["sample_file"]['name'])){

          $message = 'MutationList and Sample Files are not uploaded.\\nTry again.';

          echo "<script type='text/javascript'>alert('$message');</script>";

          echo  "<script type='text/javascript'> window.location.href = 'http://10.110.21.70/sequenomV4_1' </script>";

        }

        if(!session_id()) session_start();
        session_unset();

        ##get the user input##
        if (isset($_FILES["mutation_file"]["name"]) and isset($_FILES["sample_file"]["name"])){
        $name = $_FILES["mutation_file"]["name"];
        $_SESSION["name"] = $name;
        $tmp_name = $_FILES['mutation_file']['tmp_name'];
        $error = $_FILES['mutation_file']['error'];
        $location = '/home/scratch/';
        move_uploaded_file($tmp_name, $location.$name);


        $name2 = $_FILES["sample_file"]["name"];
        $tmp_name2 = $_FILES['sample_file']['tmp_name'];
        $error2 = $_FILES['sample_file']['error'];
        $location = '/home/scratch/';
        move_uploaded_file($tmp_name2, '/home/scratch/sequenomSample.txt');



        ##filter sequenom result##
        ob_implicit_flush(true);ob_end_flush();
        $cmd = "python /var/www/html/sequenomV4_1/filterOncoCarta.py -I /home/scratch/$name -o /home/scratch/$name.out.csv -s /home/scratch/sequenomSample.txt";
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
      }
    else if ($radioVal == "HSLung"){
      // echo("You chose the Oncocarta Assay.");


      if (empty($_FILES["mutation_file"]['name']) or empty($_FILES["sample_file"]['name'])){

        $message = 'MutationList and Sample Files are not uploaded.\\nTry again.';

        echo "<script type='text/javascript'>alert('$message');</script>";

        echo  "<script type='text/javascript'> window.location.href = 'http://10.110.21.70/sequenomV4_1' </script>";

      }

      if(!session_id()) session_start();
      session_unset();

      ##get the user input##
      if (isset($_FILES["mutation_file"]["name"]) and isset($_FILES["sample_file"]["name"])){
      $name = $_FILES["mutation_file"]["name"];
      $_SESSION["name"] = $name;
      $tmp_name = $_FILES['mutation_file']['tmp_name'];
      $error = $_FILES['mutation_file']['error'];
      $location = '/home/scratch/';
      move_uploaded_file($tmp_name, $location.$name);


      $name2 = $_FILES["sample_file"]["name"];
      $tmp_name2 = $_FILES['sample_file']['tmp_name'];
      $error2 = $_FILES['sample_file']['error'];
      $location = '/home/scratch/';
      move_uploaded_file($tmp_name2, '/home/scratch/sequenomSample.txt');



      ##filter sequenom result##
      ob_implicit_flush(true);ob_end_flush();
      $cmd = "python /var/www/html/sequenomV4_1/filterHSLung.py -I /home/scratch/$name -o /home/scratch/$name.out.csv -s /home/scratch/sequenomSample.txt";
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
    }
}
else{

    $message = 'Assay not selected.\\nTry again.';

    echo "<script type='text/javascript'>alert('$message');</script>";

    echo  "<script type='text/javascript'> window.location.href = 'http://10.110.21.70/sequenomV4_1' </script>";

}

?>

<div class="container">
    <div id="form-main">
        <div id="form-div">
            <form class="montform" enctype="multipart/form-data" action="result.php" method="post">
              <a href='http://10.110.21.70/sequenomV4_1' style="font-size: 30px;color:black;text-decoration:none">Sequenom Report Filter V4.1</a>
              <br></br>
              Program successfully completed.
              <br></br>
              Download the result file.
              <br></br>
              <div class="submit">
                      <input type="button" class="button-blue" value="Download" onclick="window.location.href='download.php'" />
              </div>
            </form>
        </div>
    </div>
</div>
