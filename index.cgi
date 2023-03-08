#!"C:\xampp\perl\bin\perl.exe"
$web_path	= 'http://localhost/videopoker';
$script   = 'http://localhost/videopoker/index.cgi';

#!/usr/bin/perl
#$web_path   = 'https://eskimo.com/~home/videopoker';
#$script     = 'https://eskimo.com/~home/cgi-bin/video_poker.cgi';

read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});

##### Split the name-value pairs
@pairs = split(/&/, $buffer);
foreach $pair (@pairs) {
   ($name, $value) = split(/=/, $pair);

   ##### Un-Webify plus signs and %-encoding
   $value =~ tr/+/ /;
   $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
   $value =~ s/<!--(.|\n)*-->//g;
   $value =~ s/</(/g;
   $value =~ s/>/)/g;
   $value =~ s/\n/ /g;
   $FORM{$name} = $value;
}

my $flag = 'N';

if ($FORM{'debug'} eq 'Discard' && $FORM{'sequence'} == 2) { 	
  $FORM{'sequence'} = 1;  
  $flag = 'Y'; 
}

if ($FORM{'carry'} > 0) {						
  $FORM{'credits'} = $FORM{'carry'}; 
}

if ($FORM{'game'} eq 'Deuces Wild') {
  $FORM{'jokers'} = 0; 
}

if ($FORM{'game'} eq 'Joker Wild') {
  $FORM{'jokers'} = 1; }
if ($FORM{'game'} eq 'Double Joker Poker') {  					$FORM{'jokers'} = 2;	}
if ($FORM{'double'} eq 'on') {  								$FORM{'sequence'} = 'd';  $FORM{'jokers'} = 0; }

print "Content-Type: text/html\n\n";
Setup();

my @hand;
my @deck;
my @deck_52;
my %values 	= ('O','15','A','14','K','13','Q','12','J','11','10','10','9','9',
			     '8','8','7','7','6','6','5','5','4','4','3','3','2','2');
my @ranks 	= ('A','2','3','4','5','6','7','8','9','10','J','Q','K');
my $credits;
my $sequence;

## independent - Draw new cards
if ($FORM{'sequence'} =~/[1d]/ && $FORM{'deck'} eq 'independent') {

  foreach my $rank (@ranks) {
    push (@deck52, $rank . 'h');
    push (@deck52, $rank . 'd');
    push (@deck52, $rank . 'c');
    push (@deck52, $rank . 's');

  }
  for ($x = 0; $x < $FORM{'jokers'}; $x++) {
     $name = 'O' . ($x + 1);
     push (@deck52, $name); 
  }
  @deck = @deck52;
  Shuffle(\@deck);
  
  ########## Get 5 cards
  my $i;
  for ($i = 1; $i <= 5; $i++) {
    push (@hand, shift @deck);
  }
}

## Use same deck until < 10
my @remain = split(/,/, $FORM{'remaining'});
my $rcnt = @remain;
if ($FORM{'sequence'} == 1 && $FORM{'deck'} eq 'one' || ($rcnt <10 && $FORM{'deck'} eq 'one') || $flag eq 'Y' ) {

  @deck = split(/,/, $FORM{'remaining'});
  if ($FORM{'remaining'} eq '' || $rcnt <10) {

    foreach my $rank (@ranks) {
      push (@deck52, $rank . 'h');
      push (@deck52, $rank . 'd');
      push (@deck52, $rank . 'c');
      push (@deck52, $rank . 's');
    }
    for ($x = 0; $x < $FORM{'jokers'}; $x++) {
       $name = 'O' . ($x + 1);
       push (@deck52, $name); 
    }

    @deck = @deck52;
    Shuffle(\@deck);
    ########## Get 5 cards
    my $i;
    for ($i = 1; $i <= 5; $i++) {
      push (@hand, shift @deck);
    }
  }
  else {
    @deck = split(/,/,$FORM{'remaining'});
    if ($FORM{'hand'} =~ m/X/) {
      ########## Get 5 cards
      my $i;
      for ($i = 1; $i <= 5; $i++) {
        push (@hand, shift @deck);
      }
    }
    else {
      @hand = split(/,/,$FORM{'hand'});
    }
  }
}

## Discards selected
if ($FORM{'sequence'} == 2 || $flag eq 'Y') {
  
  @deck = split(/,/,$FORM{'remaining'});
  @hand = split(/,/,$FORM{'hand'});
  
  my $discard = '';
  for ($i = 1; $i <= 5; $i++) {
    if ($FORM{"$i"} ne 'on') {
      $hand[$i - 1] = shift @deck;
    }
  }
}

## Done, next do a new hand
if ($FORM{'sequence'} !~ /[de]/) {
  for ($i = 0; $i <= 4; $i++) {
    if ($FORM{'sequence'} == 0) {
      $im[$i] = $web_path . '/cards/X.jpg';
    }
    else {
      if 	($hand[$i] =~ m/O[02468]/) { $im[$i] = $web_path . '/cards/' . O2 . '.jpg'; }
      elsif 	($hand[$i] =~ m/O[13579]/) { $im[$i] = $web_path . '/cards/' . O1 . '.jpg'; }
      else 						{ $im[$i] = $web_path . '/cards/' . $hand[$i] . '.jpg'; }
    }
  }

  if ($FORM{'wager'} eq '' and $FORM{'bet'} ne '') { $FORM{'wager'} = $FORM{'bet'}; }

  if ($FORM{'debug'} eq 'Discard') {   ($message, $debug, $win) = Determine(\@hand); }

  if ($FORM{'sequence'} == 2) {
    ($message, $debug, $win) = Determine(\@hand);
    $FORM{'original'} = $FORM{'credits'};
    $FORM{'credits'} =  $FORM{'credits'} + $win; 
    $FORM{'payout'} = $win;
  }
  if ($FORM{'sequence'} == 1 && $flag ne 'Y') {
    ($message, $debug, $win) = Determine(\@hand);
    $FORM{'credits'} =  $FORM{'credits'} - $FORM{'wager'}; 
  }
}
elsif  ($FORM{'sequence'} eq 'd') {
  $im[0] = $im[$i] = $web_path . '/cards/' . $hand[$i] . '.jpg'; 
  for ($i = 1; $i <= 4; $i++) {
    $im[$i] = $web_path . '/cards/X.jpg';
  }
}
elsif  ($FORM{'sequence'} eq 'e') {
  @hand = split(/,/,$FORM{'hand'});
  $im[0] = $web_path . '/cards/' . $hand[0] . '.jpg'; 
  for ($i = 1; $i <= 4; $i++) {
    if (($FORM{'pick'} - 1) == $i) {
      $im[$i] = $web_path . '/cards/' . $hand[$i] . '.jpg'; 
      
      $hand[0] =~ s/[cdsh]//;
      $hand[$i] =~ s/[cdsh]//;
       
      #win
      if ($values{$hand[0]} < $values{$hand[$i]} ) {
        $win = 2 * $FORM{'payout'};
        $FORM{'credits'} = $FORM{'original'} + 2 * $FORM{'payout'};
        $FORM{'payout'} = 2 * $FORM{'payout'};
        $FORM{'sequence'} = 2;
      }
      #tie
      elsif ($values{$hand[0]} == $values{$hand[$i]} ) {
        $FORM{'sequence'} = 2;
        $win = 'push';
      }
      #lost
      else {  
        $FORM{'credits'} = $FORM{'original'};
        $FORM{'sequence'} = 2;
      }
    }
    else {
      $im[$i] = $web_path . '/cards/X.jpg';
    }
  }
}

print "<html>\n";
print "<style type=\"text/css\">\n";
print "tr {vertical-align: 'top' }\n";
print "td {font-family: 'Arial'; vertical-align: middle; font-size: small; }\n";
print "th {font-family: 'Arial'; font-size: '14pt' }\n";
print "</style>\n";
print "<script src='https://ajax.googleapis.com/ajax/libs/jquery/2.1.4/jquery.min.js'></script>";
print '<script language="javascript" type="text/javascript">' . "\n";
print 'function imageClick(id) {
    $(id).click();
};';
print "</script>\n";
print "<body text=white bgcolor=black><center><table>\n";

my @c;
$col_color = ' bgcolor=navy align=right';
$win_color = ' bgcolor=olive align=right';
for ($i = 1; $i <= 5; $i++) {
  $c[$i] = ' align=right';
}

print "<tr><th bgcolor=gray width=200>", $FORM{'game'}, "<th width=75 bgcolor=gray align=center>1<th width=75 bgcolor=gray align=center>2";
print "<th width=75 bgcolor=gray align=center>3<th width=75 bgcolor=gray align=center>4<th width=75 bgcolor=gray align=center>5\n";

$bg = ' bgcolor="202020"';

if ($FORM{'sequence'} !~ /[12]/) {
  if ($FORM{'sequence'} == 0 && $FORM{'wager'} eq '')  { $FORM{'wager'} = 5; }
  if ($FORM{'double'} eq 'on')  { $FORM{'wager'} = ''; }
  if ($FORM{'credits'} > 0 && $FORM{'credits'} < $FORM{'wager'} )  { $FORM{'wager'} = $FORM{'credits' }; }
}

if ($FORM{'game'} eq 'Jacks or Better') {
  if ($message eq 'Royal Flush') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Royal Flush<td$c[1]>250<td$c[2]>500<td$c[3]>750<td$c[4]>1000<td$c[5]>4 0 0 0\n";
  if ($message eq 'Straight Flush') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Straight Flush<td$c[1]>50<td$c[2]>100<td$c[3]>150<td$c[4]>200<td$c[5]>250\n";
  if ($message eq 'Four of a Kind') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Four of a Kind<td$c[1]>25<td$c[2]>50<td$c[3]>75<td$c[4]>100<td$c[5]>125\n";
  if ($message eq 'Full House') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Full House<td$c[1]>9<td$c[2]>18<td$c[3]>27<td$c[4]>36<td$c[5]>45\n";
  if ($message eq 'Flush') 			{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Flush<td$c[1]>6<td$c[2]>12<td$c[3]>18<td$c[4]>24<td$c[5]>30\n";
  if ($message eq 'Straight') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Straight<td$c[1]>4<td$c[2]>8<td$c[3]>12<td$c[4]>16<td$c[5]>20\n";
  if ($message eq 'Three of a Kind') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Three of a Kind<td$c[1]>3<td$c[2]>6<td$c[3]>9<td$c[4]>12<td$c[5]>15\n";
  if ($message eq 'Two Pair') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Two Pair<td$c[1]>2<td$c[2]>4<td$c[3]>6<td$c[4]>8<td$c[5]>10\n";
  if ($message eq 'Jacks or Better') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Jacks or Better<td$c[1]>1<td$c[2]>2<td$c[3]>3<td$c[4]>4<td$c[5]>5\n";
}

if ($FORM{'game'} eq 'Aces and Faces') {
  if ($message eq 'Royal Flush') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Royal Flush<td$c[1]>250<td$c[2]>500<td$c[3]>750<td$c[4]>1000<td$c[5]>4 0 0 0\n";
  if ($message eq 'Four Aces') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Four Aces<td$c[1]>80<td$c[2]>160<td$c[3]>240<td$c[4]>320<td$c[5]>400\n";
  if ($message eq 'Straight Flush') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Straight Flush<td$c[1]>50<td$c[2]>100<td$c[3]>150<td$c[4]>200<td$c[5]>250\n";
  if ($message eq 'Four Jacks, Queens, or Kings') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Four Jacks, Queens, Kings<td$c[1]>40<td$c[2]>80<td$c[3]>120<td$c[4]>160<td$c[5]>200\n";
  if ($message eq 'Four of a Kind') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Four of a Kind<td$c[1]>25<td$c[2]>50<td$c[3]>75<td$c[4]>100<td$c[5]>125\n";
  if ($message eq 'Full House') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Full House<td$c[1]>8<td$c[2]>16<td$c[3]>24<td$c[4]>32<td$c[5]>40\n";
  if ($message eq 'Flush') 			{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Flush<td$c[1]>5<td$c[2]>10<td$c[3]>15<td$c[4]>20<td$c[5]>25\n";
  if ($message eq 'Straight') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Straight<td$c[1]>4<td$c[2]>8<td$c[3]>12<td$c[4]>16<td$c[5]>20\n";
  if ($message eq 'Three of a Kind') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Three of a Kind<td$c[1]>3<td$c[2]>6<td$c[3]>9<td$c[4]>12<td$c[5]>15\n";
  if ($message eq 'Two Pair') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Two Pair<td$c[1]>2<td$c[2]>4<td$c[3]>6<td$c[4]>8<td$c[5]>10\n";
  if ($message eq 'Jacks or Better') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Jacks or Better<td$c[1]>1<td$c[2]>2<td$c[3]>3<td$c[4]>4<td$c[5]>5\n";
}

if ($FORM{'game'} eq 'Joker Wild') {
  if ($message eq 'Royal Flush') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Royal Flush<td$c[1]>250<td$c[2]>500<td$c[3]>750<td$c[4]>1000<td$c[5]>4 0 0 0\n";
  if ($message eq 'Five of a Kind') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Five of a Kind<td$c[1]>200<td$c[2]>400<td$c[3]>600<td$c[4]>800<td$c[5]>1000\n";
  if ($message eq 'Wild Royal Flush') {	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Wild Royal Flush<td$c[1]>100<td$c[2]>200<td$c[3]>300<td$c[4]>400<td$c[5]>500\n";
  if ($message eq 'Straight Flush') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Straight Flush<td$c[1]>50<td$c[2]>100<td$c[3]>150<td$c[4]>200<td$c[5]>250\n";
  if ($message eq 'Four of a Kind') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Four of a Kind<td$c[1]>20<td$c[2]>40<td$c[3]>60<td$c[4]>80<td$c[5]>100\n";
  if ($message eq 'Full House') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Full House<td$c[1]>7<td$c[2]>14<td$c[3]>21<td$c[4]>28<td$c[5]>35\n";
  if ($message eq 'Flush') 			{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Flush<td$c[1]>5<td$c[2]>10<td$c[3]>15<td$c[4]>20<td$c[5]>25\n";
  if ($message eq 'Straight') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Straight<td$c[1]>3<td$c[2]>6<td$c[3]>9<td$c[4]>12<td$c[5]>15\n";
  if ($message eq 'Three of a Kind') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Three of a Kind<td$c[1]>2<td$c[2]>4<td$c[3]>6<td$c[4]>8<td$c[5]>10\n";
  if ($message eq 'Two Pair') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Two Pair<td$c[1]>1<td$c[2]>2<td$c[3]>3<td$c[4]>4<td$c[5]>5\n";
  if ($message eq 'Kings or Better') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Kings or Better<td$c[1]>1<td$c[2]>2<td$c[3]>3<td$c[4]>4<td$c[5]>5\n";
}

if ($FORM{'game'} eq 'Double Joker Poker') {
  if ($message eq 'Royal Flush') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Royal Flush<td$c[1]>250<td$c[2]>500<td$c[3]>750<td$c[4]>1000<td$c[5]>4 0 0 0\n";
  if ($message eq 'Wild Royal Flush') {	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Wild Royal Flush<td$c[1]>100<td$c[2]>200<td$c[3]>300<td$c[4]>400<td$c[5]>500\n";
  if ($message eq 'Five of a Kind') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Five of a Kind<td$c[1]>50<td$c[2]>100<td$c[3]>150<td$c[4]>200<td$c[5]>250\n";
  if ($message eq 'Straight Flush') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Straight Flush<td$c[1]>25<td$c[2]>50<td$c[3]>75<td$c[4]>100<td$c[5]>125\n";
  if ($message eq 'Four of a Kind') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Four of a Kind<td$c[1]>8<td$c[2]>16<td$c[3]>24<td$c[4]>32<td$c[5]>40\n";
  if ($message eq 'Full House') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Full House<td$c[1]>5<td$c[2]>10<td$c[3]>15<td$c[4]>20<td$c[5]>25\n";
  if ($message eq 'Flush') 			{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Flush<td$c[1]>4<td$c[2]>8<td$c[3]>12<td$c[4]>16<td$c[5]>20\n";
  if ($message eq 'Straight') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Straight<td$c[1]>3<td$c[2]>6<td$c[3]>9<td$c[4]>12<td$c[5]>15\n";
  if ($message eq 'Three of a Kind') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Three of a Kind<td$c[1]>2<td$c[2]>4<td$c[3]>6<td$c[4]>8<td$c[5]>10\n";
  if ($message eq 'Two Pair') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Two Pair<td$c[1]>1<td$c[2]>2<td$c[3]>3<td$c[4]>4<td$c[5]>5\n";
}

if ($FORM{'game'} eq 'Deuces Wild') {
  if ($message eq 'Royal Flush') 	{	$c[$FORM{'wager'}] = $win_color; }			else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Royal Flush<td$c[1]>250<td$c[2]>500<td$c[3]>750<td$c[4]>1000<td$c[5]>4 0 0 0\n";
  if ($message eq 'Four Deuces') 	{	$c[$FORM{'wager'}] = $win_color; }			else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Four Deuces<td$c[1]>200<td$c[2]>400<td$c[3]>600<td$c[4]>800<td$c[5]>1000\n";
  if ($message eq 'Wild Royal Flush') {	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Wild Royal Flush<td$c[1]>25<td$c[2]>50<td$c[3]>75<td$c[4]>100<td$c[5]>125\n";
  if ($message eq 'Five of a Kind') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Five of a Kind<td$c[1]>15<td$c[2]>30<td$c[3]>45<td$c[4]>60<td$c[5]>75\n";
  if ($message eq 'Straight Flush') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Straight Flush<td$c[1]>9<td$c[2]>18<td$c[3]>27<td$c[4]>36<td$c[5]>45\n";
  if ($message eq 'Four of a Kind') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Four of a Kind<td$c[1]>5<td$c[2]>10<td$c[3]>15<td$c[4]>20<td$c[5]>25\n";
  if ($message eq 'Full House') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Full House<td$c[1]>3<td$c[2]>6<td$c[3]>9<td$c[4]>12<td$c[5]>15\n";
  if ($message eq 'Flush') 			{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Flush<td$c[1]>2<td$c[2]>4<td$c[3]>6<td$c[4]>8<td$c[5]>10\n";
  if ($message eq 'Straight') 		{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr><td>Straight<td$c[1]>2<td$c[2]>4<td$c[3]>6<td$c[4]>8<td$c[5]>10\n";
  if ($message eq 'Three of a Kind') 	{	$c[$FORM{'wager'}] = $win_color; }		else {     $c[$FORM{'wager'}] = $col_color; }
  print "<tr$bg><td>Three of a Kind<td$c[1]>1<td$c[2]>2<td$c[3]>3<td$c[4]>4<td$c[5]>5\n";
}

my $border;
my $td1 = '<td align=center valign=center width=280>';
my $td3 = '<td align=center valign=center width=150>';
my $td5 = '<td width=75>';
my $td6 = "<td valign=center align=center bgcolor=maroon width=75>" . $FORM{'credits'} . " Credits";

if ($FORM{'sequence'} == 2 && ($win > 0 || $win eq 'push')) {
  if ($win > 0) {
    $border = 'olive';
    $td5 = "<td width=75 valign=center align=center bgcolor=olive>Won $win";
  }
  else {
    $border = 'blue';
    $td5 = "<td width=75 valign=center align=center bgcolor=blue>Push";
  }
}
elsif ($FORM{'sequence'} == 2)  {
  $border = 'red';
  $td5 = "<td width=75 valign=center align=center bgcolor=red>Lost";
}
else {
  if ($message ne '') 	{    $border = 'olive';  }
  else 			{    $border = 'navy';  }
}

print "</table></center>\n";
print "<br>";
print "<form method=POST action=\"$script\">\n";

if ($FORM{'sequence'} == 2) {
  if ($FORM{'credits'} > 0) {
    $td1 .= "Main Menu <input name=mainmenu type=checkbox>";
    if ($win > 0 || $win eq 'push') {
      $td1 .= "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Double <input name=double type=checkbox>";
    }
    $td3 .= "<input type=submit value='Continue'>";
    $FORM{'sequence'} = -1;
  }
  else {
    print "<input type=hidden name=mainmenu value='on'>\n";
    $td3 .= "<input type=submit value='Main Menu'>";
  }
}
if ($FORM{'sequence'} == 1) {
  $td3 .= "<input type=submit value='Draw Cards'>";
}
my @CH;
if ($FORM{'sequence'} == 0 && $FORM{'double'} ne 'on') {
  $td3 .= "<input type=submit value='Show Cards'>";
  $ch[$FORM{'wager'}] = 'checked';
  if ($FORM{'credits'} >= 1) {  $td1 .= "Bet&nbsp;&nbsp;&nbsp;&nbsp;1<input type=radio name='wager' value='1' $ch[1]>&nbsp;&nbsp;&nbsp;&nbsp;"; }
  if ($FORM{'credits'} >= 2) {  $td1 .= "2<input type=radio name='wager' value='2' $ch[2]>&nbsp;&nbsp;&nbsp;&nbsp;"; }
  if ($FORM{'credits'} >= 3) {  $td1 .= "3<input type=radio name='wager' value='3' $ch[3]>&nbsp;&nbsp;&nbsp;&nbsp;"; }
  if ($FORM{'credits'} >= 4) {  $td1 .= "4<input type=radio name='wager' value='4' $ch[4]>&nbsp;&nbsp;&nbsp;&nbsp;"; }
  if ($FORM{'credits'} >= 5) {  $td1 .= "5<input type=radio name='wager' value='5' $ch[5]>"; }
}
if ($FORM{'double'} eq 'on') {
  $td3 .= "<input type=submit value='Show Card'>";
}

print "<center><table>\n";
print "<tr>$td1$td2$td3$td4$td5$td6\n";
print "</table></center><br>\n";

print "<center><table border=5 bordercolor=$border cellpadding=4 bgcolor='006666'><tr><td><table>\n";

if ($FORM{'sequence'} == 1) {
  print "<tr>\n";
  print "<td align=center><font color=white>Hold </font><input id='c1' name=1 type=checkbox>\n";
  print "<td align=center><font color=white>Hold </font><input id='c2' name=2 type=checkbox>\n";
  print "<td align=center><font color=white>Hold </font><input id='c3' name=3 type=checkbox>\n";
  print "<td align=center><font color=white>Hold </font><input id='c4' name=4 type=checkbox>\n";
  print "<td align=center><font color=white>Hold </font><input id='c5' name=5 type=checkbox>\n";
}

elsif ($FORM{'sequence'} eq 'd') {
  print "<tr>\n";
  print "<td>\n";
  print "<td align=center><font color=white>Select </font><input id='c2' name=pick value=2 type=radio>\n";
  print "<td align=center><font color=white>Select </font><input id='c3' name=pick value=3 type=radio>\n";
  print "<td align=center><font color=white>Select </font><input id='c4' name=pick value=4 type=radio>\n";
  print "<td align=center><font color=white>Select </font><input id='c5' name=pick value=5 type=radio>\n";
  print "<input type=hidden name=double_hand value=\"", join(',',@hand), "\">\n";
}
else {
  print "<tr><td colspan=5>&nbsp;\n";
}

print "<tr>\n";
print "<td>&nbsp;<img onclick=\"imageClick('#c1')\" src=\"$im[0]\">\n";
print "<td>&nbsp;<img onclick=\"imageClick('#c2')\" src=\"$im[1]\">\n";
print "<td>&nbsp;<img onclick=\"imageClick('#c3')\" src=\"$im[2]\">\n";
print "<td>&nbsp;<img onclick=\"imageClick('#c4')\" src=\"$im[3]\">\n";
print "<td>&nbsp;<img onclick=\"imageClick('#c5')\" src=\"$im[4]\">\n";

print "</table></table></center>\n";

if ($FORM{'double'} eq 'on')  { $FORM{'sequence'} = 'e'; }
else {  $FORM{'sequence'}++;  }

print "<input type=hidden name=deck value='", $FORM{'deck'}, "'>\n";
print "<input type=hidden name=game value='", $FORM{'game'}, "'>\n";
print "<input type=hidden name=bet value='", $FORM{'wager'}, "'>\n";
print "<input type=hidden name=payout value='", $FORM{'payout'}, "'>\n";
print "<input type=hidden name=original value='", $FORM{'original'}, "'>\n";
print "<input type=hidden name=jokers value='", $FORM{'jokers'}, "'>\n";
print "<input type=hidden name=credits value='", $FORM{'credits'}, "'>\n";
print "<input type=hidden name=sequence value='", $FORM{'sequence'}, "'>\n";
print "<input type=hidden name=debug value='", $FORM{'debug'}, "'>\n";
print "<input type=hidden name=remaining value=\"", join(',',@deck), "\">\n";
print "<input type=hidden name=hand value=\"", join(',',@hand), "\">\n";
print "<input type=hidden name=status value=\"on\">\n";
print "<input type=hidden name=style value=\"Hold\">\n";

if ($FORM{'debug'} eq 'Show' || $FORM{'debug'} eq 'Discard') {
  foreach $ele (keys %FORM) {
    print "<hr>$ele = ", $FORM{"$ele"}, "\n";
  }
  print "<hr>$debug\n";
}

print "</form></body>\n";
print "</html>\n";

exit;

########## SUB: Fisher-Yates Array Shuffle
sub Shuffle {
  my $array = shift;
  my $i;
  for ($i = @$array; --$i; ) {
    my $j = int rand ($i+1);
    next if $i == $j;
    @$array [$i,$j] = @$array[$j,$i];
  }
}

########## SUB: Determine the hand
sub Determine {
  my $h = shift;
  my $i = 0;
  my $jok = 0;
  undef($determination);

  my @array = @$h;
  my $card;
  my $suit;
  my $value;

  my @str;
  my @c;
  my @s;
  my @v;
  
  my $inc = 0;
  if ($FORM{'game'} eq 'Deuces Wild') {
    for ($i = 0; $i <= 5; $i++) {
      if($array[$i] =~ /^2/) {
        $inc++;
        $array[$i] = 'O' . $inc;
      }
    }
  }
  
  ### sort the Hand based on card rank - because a hash is used, all cards must be distinctly named (i.e. 1 deck)
  my %hash;
  foreach $ele (@array) {
    $card = $ele;
    $card =~ s/[hscdj]$//;
    $hash{"$ele"} = $values{"$card"};
  }

  my @sorted;
  foreach $ele (sort {$hash{$b} <=> $hash{$a}} (keys(%hash))) {
    push (@sorted, $ele);
  }

  foreach $ele (@sorted) {
    if ($ele =~ /O[0-9]+/) {
      $jok++;    
    }
    else {
      @str = split(//,$ele);
      $card = $ele;
      $card =~ s/[hscdj]$//;

      push (@c,$card);
      push (@s,pop(@str));
      push (@v,$values{$card});
    }
  }
  
  my $pair      = 'N';
  my $twopair   = 'N';
  my $threekind = 'N';
  my $fullhouse	= 'N';
  my $fourkind  = 'N';
  my $fivekind 	= 'N';
  my $flush 	  = 'N';
  my $royal   	= 'N';
  my $st_flush 	= 'N';
  my $straight 	= 'N';
  my $fourdeuce	= 'N';
  my $fourace 	= 'N';
  my $fourface 	= 'N';
  my $jacks 	  = 'N';

  my %pair;
  my $cnt = 0;  # number of unique rankings in hand

  foreach $ele (@c) {
    if (!defined($pair{"$ele"})) {
      $cnt++;
    }
    $pair{"$ele"}++;
  }
  
  ## STRAIGHT
  my @t = @v;
  my @th = @c;  
  # find lowest/highest values
  my $low_card = pop @t;
  my $high_card = shift @th;
  my $array = '';
  foreach $ele (@v) {
    $array .= ($ele - $low_card);
  }
  if (length($array) == 5) {
    if ($array =~ /^43210$/) {
      $straight = 'Y';
    }
  }
  if (length($array) == 4) {
    if ($array =~ /^4320$/ || $array =~ /^4310$/ || $array =~ /^4210$/ || $array =~ /^3210$/) {
      $straight = 'Y';
    }
  }
  if (length($array) == 3) {
    if ($array =~ /^430$/ || $array =~ /^420$/ || $array =~ /^410$/ ||
	$array =~ /^320$/ || $array =~ /^310$/ || 
	$array =~ /^210$/) {
      $straight = 'Y';
    }
  }
  
  ## Straight - if Ace is low
  $ace_low_array = '';
  @t = @v;
  if ($t[0] == 14) {
    shift @t;
    push (@t, "1");
    $low_card = 1;
  }
  foreach $ele (@t) {
    $ace_low_array .= ($ele - $low_card);
  }
  if (length($ace_low_array) == 5) {
    if ($ace_low_array =~ /^43210$/) {
      $straight = 'Y';
    }
  }
  if (length($ace_low_array) == 4) {
    if ($ace_low_array =~ /^4320$/ || $ace_low_array =~ /^4310$/ || $ace_low_array =~ /^4210$/ || $ace_low_array =~ /^3210$/) {
      $straight = 'Y';
    }
  }
  if (length($ace_low_array) == 3) {
    if ($ace_low_array =~ /^430$/ || $ace_low_array =~ /^420$/ || $ace_low_array =~ /^410$/ ||
	      $ace_low_array =~ /^320$/ || $ace_low_array =~ /^310$/ || 
	      $ace_low_array =~ /^210$/) {
      $straight = 'Y';
    }
  }
  
  ## FLUSH
  if (($s[0] eq $s[1] && $s[0] eq $s[2] && $s[0] eq $s[3] && $s[0] eq $s[4] && $jok == 0) ||
      ($s[0] eq $s[1] && $s[0] eq $s[2] && $s[0] eq $s[3] && $jok == 1) ||
      ($s[0] eq $s[1] && $s[0] eq $s[2] && $jok == 2)) {
    $flush = 'Y';
  }
  
  ## ROYAL
  my $royal_array;
  my $natural = 'N';
  foreach $ele (@c) {
    $royal_array .= $ele;
  }
  if ($royal_array =~ /^AKQJ10$/ || 
   	$royal_array =~ /^KQJ10$/ ||
    $royal_array =~ /^AQJ10$/ ||
    $royal_array =~ /^AKJ10$/  ||
    $royal_array =~ /^AKQ10$/ ||
    $royal_array =~ /^AKQJ/  ||
    $royal_array =~ /^AKQ$/  || $royal_array =~ /^AKJ$/  || $royal_array =~ /^AK10$/ || 
    $royal_array =~ /^AQJ$/  || $royal_array =~ /^AQ10$/  || $royal_array =~ /^AJ10$/  ||
    $royal_array =~ /^KQJ$/ || $royal_array =~ /^KQ10$/ ||	$royal_array =~ /^KJ10$/  ||
    $royal_array =~ /^QJ10$/ ) {
	
    $royal = 'Y';
      if ( $royal_array =~ /^AKQJ10$/) { $natural = 'Y'; } 
  }

  ## PAIRS AND FULL HOUSE
  $ace_king = 'N';
  my $old;
  foreach $ele (keys %pair) {

    if (($pair{"$ele"} + $jok) == 2 && $cnt == 4) {
      $pair = 'Y';
      if ($ele =~ m/[AK]/) 	{ $ace_king = 'Y'; }
      if ($ele =~ m/[AKQJ]/) 	{ $jacks = 'Y'; }
    }
    if (($pair{"$ele"} + $jok) == 2 && $cnt == 3) {
      foreach $e (keys %pair) {
        if (($pair{"$e"} + $jok) == 2 && $e ne $ele) {
          $twopair = 'Y';
        }
      }
    }
    if (($pair{"$ele"} + $jok) == 3) {
      $threekind = 'Y';
    }
    if (($pair{"$ele"} + $jok) == 3 && $cnt == 2) {
      foreach $e (keys %pair) {
	      $fullhouse = 'Y';
      }
    }
    if (($pair{"$ele"} + $jok) == 4) {
      $fourkind = 'Y';
      if ($ele =~ m/A/) 		{ $fourace = 'Y'; }
      if ($ele =~ m/[KQJ]/) 	{ $fourface = 'Y'; }
    }
    if (($pair{"$ele"} + $jok) == 5) {
      $fivekind = 'Y';
      if ($jok == 4 && $FORM{'game'} eq 'Deuces Wild') { $fourdeuce = 'Y'; }
    }
  }
  
  my $win = 0;
  
  if ($FORM{'game'} eq 'Jacks or Better') {
    if ($royal eq 'Y' && $flush eq 'Y' && $straight eq 'Y' && $natural eq 'Y') 	
						{ $determination = "Royal Flush";			if ($FORM{'wager'} == 5) { $win = 4000; } else { $win = 250 * $FORM{'wager'}; } }
    elsif ($straight eq 'Y' && $flush eq 'Y') 	
						{ $determination = "Straight Flush"; 			$win = 50 * $FORM{'wager'}; }
    elsif ($fourkind eq 'Y') 		{ $determination = "Four of a Kind"; 			$win = 25 * $FORM{'wager'}; }
    elsif ($fullhouse eq 'Y') 		{ $determination = "Full House"; 			$win = 9 * $FORM{'wager'}; }
    elsif ($flush eq 'Y') 		{ $determination = "Flush"; 				$win = 6 * $FORM{'wager'}; }
    elsif ($straight eq 'Y') 		{ $determination = "Straight"; 				$win = 4 * $FORM{'wager'}; }
    elsif ($threekind eq 'Y') 		{ $determination = "Three of a Kind"; 		$win = 3 * $FORM{'wager'}; }
    elsif ($twopair eq 'Y') 		{ $determination = "Two Pair";   				$win = 2 * $FORM{'wager'}; }
    elsif ($pair eq 'Y' && $jacks eq 'Y') 		
	  					{ $determination = "Jacks or Better"; 		$win = 1 * $FORM{'wager'}; }
    else { $determination = "";  }
  }
  
  if ($FORM{'game'} eq 'Aces and Faces') {
    if ($royal eq 'Y' && $flush eq 'Y' && $straight eq 'Y' && $natural eq 'Y') 	
						{ $determination = "Royal Flush";			if ($FORM{'wager'} == 5) { $win = 4000; } else { $win = 250 * $FORM{'wager'}; } }
    elsif ($fourace eq 'Y') 		{ $determination = "Four Aces";	 			$win = 80 * $FORM{'wager'}; }
    elsif ($straight eq 'Y' && $flush eq 'Y') 	
						{ $determination = "Straight Flush"; 			$win = 50 * $FORM{'wager'}; }
    elsif ($fourface eq 'Y') 		{ $determination = "Four Jacks, Queens, or Kings";	$win = 400 * $FORM{'wager'}; }						
    elsif ($fourkind eq 'Y') 		{ $determination = "Four of a Kind"; 			$win = 25 * $FORM{'wager'}; }
    elsif ($fullhouse eq 'Y') 		{ $determination = "Full House"; 			$win = 8 * $FORM{'wager'}; }
    elsif ($flush eq 'Y') 		{ $determination = "Flush"; 				$win = 5 * $FORM{'wager'}; }
    elsif ($straight eq 'Y') 		{ $determination = "Straight"; 				$win = 4 * $FORM{'wager'}; }
    elsif ($threekind eq 'Y') 		{ $determination = "Three of a Kind"; 		$win = 3 * $FORM{'wager'}; }
    elsif ($twopair eq 'Y') 		{ $determination = "Two Pair";   				$win = 2 * $FORM{'wager'}; }
    elsif ($pair eq 'Y' && $jacks eq 'Y') 		
	  					{ $determination = "Jacks or Better"; 		$win = 1 * $FORM{'wager'}; }
    else { $determination = "";  }
  }
  
  if ($FORM{'game'} eq 'Joker Wild') {
    if ($royal eq 'Y' && $flush eq 'Y' && $straight eq 'Y' && $natural eq 'Y') 	
						{ $determination = "Royal Flush";			if ($FORM{'wager'} == 5) { $win = 4000; } else { $win = 250 * $FORM{'wager'}; } }    
    elsif ($fivekind eq 'Y') 		{ $determination = "Five of a Kind"; 			$win = 200 * $FORM{'wager'}; }
    elsif ($royal eq 'Y' && $flush eq 'Y' && $straight eq 'Y') 	
						{ $determination = "Wild Royal Flush";		$win = 100 * $FORM{'wager'}; }
    elsif ($straight eq 'Y' && $flush eq 'Y') 	
						{ $determination = "Straight Flush"; 			$win = 50 * $FORM{'wager'}; }
    elsif ($fourkind eq 'Y') 		{ $determination = "Four of a Kind"; 			$win = 20 * $FORM{'wager'}; }
    elsif ($fullhouse eq 'Y') 		{ $determination = "Full House"; 			$win = 7 * $FORM{'wager'}; }
    elsif ($flush eq 'Y') 		{ $determination = "Flush"; 				$win = 5 * $FORM{'wager'}; }
    elsif ($straight eq 'Y') 		{ $determination = "Straight"; 				$win = 3 * $FORM{'wager'}; }
    elsif ($threekind eq 'Y') 		{ $determination = "Three of a Kind"; 		$win = 2 * $FORM{'wager'}; }
    elsif ($twopair eq 'Y') 		{ $determination = "Two Pair";   				$win = 1 * $FORM{'wager'}; }
    elsif ($pair eq 'Y' && $ace_king eq 'Y') 		
	  					{ $determination = "Kings or Better"; 		$win = 1 * $FORM{'wager'}; }
    else { $determination = "";  }
  }
  
  if ($FORM{'game'} eq 'Double Joker Poker') {
    if ($royal eq 'Y' && $flush eq 'Y' && $straight eq 'Y' && $natural eq 'Y') 	
						{ $determination = "Royal Flush";			if ($FORM{'wager'} == 5) { $win = 4000; } else { $win = 250 * $FORM{'wager'}; } }    
    elsif ($royal eq 'Y' && $flush eq 'Y' && $straight eq 'Y') 	
						{ $determination = "Wild Royal Flush";		$win = 100 * $FORM{'wager'}; }
    elsif ($fivekind eq 'Y') 		{ $determination = "Five of a Kind"; 			$win = 50 * $FORM{'wager'}; }
    elsif ($straight eq 'Y' && $flush eq 'Y') 	
						{ $determination = "Straight Flush"; 			$win = 25 * $FORM{'wager'}; }
    elsif ($fourkind eq 'Y') 		{ $determination = "Four of a Kind"; 			$win = 8 * $FORM{'wager'}; }
    elsif ($fullhouse eq 'Y') 		{ $determination = "Full House"; 			$win = 5 * $FORM{'wager'}; }
    elsif ($flush eq 'Y') 		{ $determination = "Flush"; 				$win = 4 * $FORM{'wager'}; }
    elsif ($straight eq 'Y') 		{ $determination = "Straight"; 				$win = 3 * $FORM{'wager'}; }
    elsif ($threekind eq 'Y') 		{ $determination = "Three of a Kind"; 		$win = 2 * $FORM{'wager'}; }
    elsif ($twopair eq 'Y') 		{ $determination = "Two Pair";   				$win = 1 * $FORM{'wager'}; }
    else { $determination = "";  }
  }
  
  elsif ($FORM{'game'} eq 'Deuces Wild') {
    if ($royal eq 'Y' && $flush eq 'Y' && $straight eq 'Y' && $natural eq 'Y') 	
						{ $determination = "Royal Flush";			if ($FORM{'wager'} == 5) { $win = 4000; } else { $win = 250 * $FORM{'wager'}; } }    
    elsif ($fourdeuce eq 'Y') 	{ $determination = "Four Deuces"; 			$win = 200 * $FORM{'wager'}; }
    elsif ($royal eq 'Y' && $flush eq 'Y' && $straight eq 'Y') 	
						{ $determination = "Wild Royal Flush";		$win = 25 * $FORM{'wager'}; }
    elsif ($fivekind eq 'Y') 		{ $determination = "Five of a Kind"; 			$win = 15 * $FORM{'wager'}; }
    elsif ($straight eq 'Y' && $flush eq 'Y') 	
						{ $determination = "Straight Flush"; 			$win = 9 * $FORM{'wager'}; }
    elsif ($fourkind eq 'Y') 		{ $determination = "Four of a Kind"; 			$win = 5 * $FORM{'wager'}; }
    elsif ($fullhouse eq 'Y') 		{ $determination = "Full House"; 			$win = 3 * $FORM{'wager'}; }
    elsif ($flush eq 'Y') 		{ $determination = "Flush"; 				$win = 2 * $FORM{'wager'}; }
    elsif ($straight eq 'Y') 		{ $determination = "Straight"; 				$win = 2 * $FORM{'wager'}; }
    elsif ($threekind eq 'Y') 		{ $determination = "Three of a Kind"; 		$win = 1 * $FORM{'wager'}; }
    else { $determination = "";  }
  }
  

  
  $debug =	"suits: " . join(',',@s) . "; " .
		"values: " . join(',',@v) . "; " . 
		"cards: " . join(',',@c) . "\n" .
		"distinct = $cnt; Array = $array; Royal Array $royal_array; ALA: $ace_low_array\n"  .
		"pair($pair); 2-P($twopair); 3-K($threekind); 4-K($fourkind); Full($fullhouse); Flush($flush)\n" .
                "Royal($royal); stflush($st_flush); straight($straight); 5-K($fivekind); Jok($jok); CNT($cnt); 4-Duece($fourdeuce)\n\n";

  if ($royal eq 'Y' && $flush eq 'Y' && $straight eq 'Y' && $natural eq 'Y' && $FORM{'wager'} == 5) { $win = $win +2750; }

  return($determination, $debug, $win);
}

sub Setup {

  if ($FORM{'mainmenu'} eq 'on' || $FORM{'game'} eq '') {

  $cred = $FORM{'credits'};
  if ($FORM{'credits'} > 0) {
    $custom = "<option selected>" . $FORM{'credits'};
  }
  else {
    $custom = "<option selected>100";
  }

$menu = <<HTML_END;

<html>
  <style type="text/css">
    body {font-family: Arial}
    body {font-size: 9pt}
  </style>
  <head>
    <title>Video Poker</title>
  </head>
  <body text=white bgcolor=black>
    <center><h1>Video Poker</h1>

    Version 1.0&nbsp;&nbsp;&nbsp;&nbsp;<font size=2pt color=lightblue>&#169; Jan-Feb 2004 / Jan 2023 SCE</font><br><br>

    <form method=POST action="$script">
    <table border=1>
    <tr>
      <td><font size=4pt face="comic sans ms" color=lightblue>Credit </font>
      <td><select name=credits>
          $custom
          </select>
    <tr>
      <td><font size=4pt face="comic sans ms" color=lightblue>Game</font>
      <td><select name=game>
          <option>Aces and Faces
          <option>Deuces Wild
          <option>Double Joker Poker
          <option>Jacks or Better
          <option>Joker Wild
          </select>
    </table>
    <br><input type=submit value=Start>
    <input type=hidden name=sequence value=0>
    <input type=hidden name=wager value=5>
    <input type=hidden name=status value="on">
    <input type=hidden name=deck value=independent>
    </form></center>

    <font color=lightblue>Welcome to this suite of Video Poker games written in Perl featuring the "Iraqi War Most-wanted" deck of cards. 
    New games start with 100 credits.  The payout tables and game-play accurately emulate the casino games.</font><br><br>

    <u><b>Aces and Faces</b></u><br>
    Aces and Faces is a Jacks or Better variation that has a higher payout for certain Four-of-a-Kinds. This 
    bonus is partially offset by a lower payout for a Full House or Flush. The long-term payback for this machine 
    is 99.85%, which is slightly better than Jacks or Better. <br><br>

    <u><b>Deuces Wild</b></u><br>
    In Deuces Wild, all four 2s are wild cards. They can represent any card value or suit that is necessary to complete a 
    winning hand. Since it is easier to get good hands, the payout table has been adjusted from a standard Jacks or Better
    payout table. Also, because there are four wild cards, new winning hands have been added to the payout table: Four 
    Deuces, Wild Royal Flush and Five of a Kind. Players using optimal strategy on an original full-pay version of Deuces 
    Wild can expect a long term payout of 100.76%, which is one of the few games in the casino where the player has an 
    advantage over the house.<br><br>

    <u><b>Double Joker Poker</b></u><br>
    Double Joker poker uses a 54-card deck which includes two wild Jokers. This game offers a long-term payback 
    of 99.96% using optimal strategy.<br><br>

    <u><b>Jacks or Better</b></u><br>
    The original Video Poker machines were based on Five Card Draw Poker and paid off on Two Pair or better. Because 
    of the low overall payoff the machines evolved into Jacks or Better Video Poker which pays even on a high pair. Jacks
    or Better has become the popular standard from which all other variations have grown. The long-term payout for a 
    machine with this pay table is 99.54% using optimal strategy. <br><br>

    <u><b>Joker Wild</b></u><br>
    This game uses a 53-card deck that includes one wild Joker. Joker Wild offers a long-term payback of 100.6%. 
    Beware of Joker Wild machines with a minimum paying hand of 2 Pair, these machines offer a long term payback 
    of below 99%. <br><br>
  </body>
</html>

HTML_END

    print $menu;
    exit;
  }
}
