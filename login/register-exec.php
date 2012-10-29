<?php
// #################################################################################
// #################################################################################
// Voseq login/register-exec.php
// Copyright (c) 2006, PHPSense.com
// All rights reserved.
//
// Modified by Carlos Pe�a & Tobias Malm
// Mods: added admin-session and sha1 - encryption for passwords
//
// Script overview: stores the new user details
// #################################################################################

header('Content-type: text/html; charset=utf8');

	//check admin login session
	include'auth-admin.php';
	
	//Start session
	session_start();
	
	//Include database connection details

	ob_start();//Hook output buffer - disallows web printing of file info...
	require_once'../conf.php';
	ob_end_clean();//Clear output buffer//includes
	//Array to store validation errors
	$errmsg_arr = array();
	
	//Validation error flag
	$errflag = false;
	
	//Connect to mysql server
	$link = mysql_connect($host, $user, $pass);
	if(!$link) {
		die('Failed to connect to server: ' . mysql_error());
	}
	
	//Select database
	$db = mysql_select_db($db);
	if(!$db) {
		die("Unable to select database");
	}
	if( function_exists(mysql_set_charset) ) {
		mysql_set_charset("utf8");
	}

	
	//Function to sanitize values received from the form. Prevents SQL injection
	function clean($str) {
		$str = @trim($str);
		if(get_magic_quotes_gpc()) {
			$str = stripslashes($str);
		}
		return mysql_real_escape_string($str);
	}
	
	//Sanitize the POST values
	$fname = clean($_POST['fname']);
	$lname = clean($_POST['lname']);
	$login = clean($_POST['login']);
	$password = clean($_POST['password']);
	$cpassword = clean($_POST['cpassword']);
	$adminyesno = clean($_POST['admin']);
	
	//Input Validations
	if($fname == '') {
		$errmsg_arr[] = 'First name missing';
		$errflag = true;
	}
	if($lname == '') {
		$errmsg_arr[] = 'Last name missing';
		$errflag = true;
	}
	if($login == '') {
		$errmsg_arr[] = 'Login ID missing';
		$errflag = true;
	}
	if($password == '') {
		$errmsg_arr[] = 'Password missing';
		$errflag = true;
	}
	if($cpassword == '') {
		$errmsg_arr[] = 'Confirm password missing';
		$errflag = true;
	}
	if( strcmp($password, $cpassword) != 0 ) {
		$errmsg_arr[] = 'Passwords do not match';
		$errflag = true;
	}
	
	//Check for duplicate login ID
	if($login != '') {
		$qry = "SELECT * FROM ". $p_ . "members WHERE login='$login'";
		$result = mysql_query($qry);
		if($result) {
			if(mysql_num_rows($result) > 0) {
				$errmsg_arr[] = 'Login ID already in use';
				$errflag = true;
			}
			@mysql_free_result($result);
		}
		else {
			die("Query failed");
		}
	}
	
	//If there are input validations, redirect back to the registration form
	if($errflag) {
		$_SESSION['ERRMSG_ARR'] = $errmsg_arr;
		session_write_close();
		header("location: register-form.php");
		exit();
	}

	//Create INSERT query
	$qry = "INSERT INTO ". $p_ . "members(firstname, lastname, login, passwd, admin) VALUES('$fname','$lname','$login','".sha1($_POST['password'])."','$adminyesno')";
	$result = @mysql_query($qry);
	
	//Check whether the query was successful or not
	if($result) {
		header("location: register-success.php");
		exit();
	}else {
		die("Query failed");
	}
?>
