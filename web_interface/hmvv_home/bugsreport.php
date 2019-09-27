<head>
    <title>HMVV3 Feedback and Bug Reporting Tool</title>
    <link rel="stylesheet" href="form.css" >
</head>
<body style="background-color:grey;">
<div id="result-main">
<p> HMVV3 Reported Feedback and Bugs </font> </p>
<div class="image_table">
     <table class="zui-table" >
        <thead>
          <tr>
               <th>ID</th>
               <th>message</th>
               <th>timeUpdated</th>
               <th>Solution</th>
               <th>Closed</th>
              <th>Image</th>
          </tr>
           <thead>
              <tbody>
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


     $query = "SELECT * FROM hmvv3_bugs ORDER BY bugID DESC, closed DESC";
     $result = mysqli_query($connect, $query);
     while($row = mysqli_fetch_array($result))
     {
          echo '
               <tr>
                    <td>' . htmlspecialchars($row['bugID'] ) . '</td>
                    <td>' . htmlspecialchars($row['message'] ) . '</td>
                    <td>' . htmlspecialchars($row['timeUpdated'] ) . '</td>
                    <td>' . htmlspecialchars($row['solution'] ) . '</td>
                    <td>' . htmlspecialchars($row['closed'] ) . '</td>
                    <td>';
                       echo '<a href="http://10.110.21.70/hmvv3/images/'.$row['bugURL'].'">Link</a>
                    </td>
               </tr>
            ';
     }
     ?>
   </tbody>
     </table>
   </div>
   </div>
</body>
