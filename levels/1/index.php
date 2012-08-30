<html>
  <head>
    <title>Guessing Game</title>
  </head>
  <body>
    <h1>Welcome to the Guessing Game!</h1>
    <p>
      Guess the secret combination below, and if you get it right,
      you'll get the password to the next level!
    </p>
    <?php
      $filename = 'secret-combination.txt';
      extract($_GET);
      if (isset($attempt)) {
        $combination = trim(file_get_contents($filename));
        if ($attempt === $combination) {
          echo "<p>How did you know the secret combination was" .
               " $combination!?</p>";
          $next = file_get_contents('level02-password.txt');
          echo "<p>You've earned the password to the access Level 2:" .
               " $next</p>";
        } else {
          echo "<p>Incorrect! The secret combination is not $attempt</p>";
        }
      }
    ?>
    <form action="#" method="GET">
      <p><input type="text" name="attempt"></p>
      <p><input type="submit" value="Guess!"></p>
    </form>
  </body>
</html>
