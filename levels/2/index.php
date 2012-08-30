<?php
  session_start();

  if ($_FILES["dispic"]["error"] > 0) {
    echo "<p>Error: " . $_FILES["dispic"]["error"] . "</p>";
  }
  else
  {
    $dest_dir = "uploads/";
    $dest = $dest_dir . basename($_FILES["dispic"]["name"]);
    $src = $_FILES["dispic"]["tmp_name"];
    if (move_uploaded_file($src, $dest)) {
      $_SESSION["dispic_url"] = $dest;
      chmod($dest, 0644);
      echo "<p>Successfully uploaded your display picture.</p>";
    }
  }

  $url = "https://upload.wikimedia.org/wikipedia/commons/f/f8/" .
         "Question_mark_alternate.svg";
  if (isset($_SESSION["dispic_url"])) {
    $url = $_SESSION["dispic_url"];
  }

?>

<html>
  <head>
    <title>Welcome to the CTF!</title>
  </head>
  <body>
    <center>
      <h1>Welcome to the CTF Social Network!</h1>
      <div>
        <img src=<?php echo $url; ?> />
        <?php
          if (!isset($_SESSION["dispic_url"])) {
            echo "<p>Oh, looks like you don't have a profile image" .
                 " -- upload one now!</p>";
          }
        ?>
        <form action="" method="post" enctype="multipart/form-data">
          <input type="file" name="dispic" size="40" />
          <input type="submit" value="Upload!">
        </form>

        <p>
           Password for Level 3 (accessible only to members of the club):
           <a href="password.txt">password.txt</a>
        </p>
      </div>
    </center>
  </body>
</html>
