<head>
    <title>HMVV3 Bug Reporting Tool</title>
    <link rel="stylesheet" href="form.css" >
</head>
<body style="background-color:grey;">
<div id="result-main">
<p> HMVV3 Reported Bugs </font> </p>
<div class="image_table">
     <table class="zui-table" >
        <thead>
          <tr>
               <th>bugID</th>
               <th>message</th>
               <th>timeUpdated</th>
               <th>Image</th>
          </tr>
           <thead>
              <tbody>
     <?php
     date_default_timezone_set('GMT');
     session_start();
     $connect = mysqli_connect("localhost", "", "", "");
     $query = "SELECT * FROM hmvv3_bugs ORDER BY bugID DESC";
     $result = mysqli_query($connect, $query);
     while($row = mysqli_fetch_array($result))
     {
          echo '
               <tr>
                    <td>' . htmlspecialchars($row['bugID'] ) . '</td>
                    <td>' . htmlspecialchars($row['message'] ) . '</td>
                    <td>' . htmlspecialchars($row['timeUpdated'] ) . '</td>
                    <td>
                       <img alt="" src="data:image/png;base64,'.base64_encode($row['bugImage'] ).'" height="100" width="100" />
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
