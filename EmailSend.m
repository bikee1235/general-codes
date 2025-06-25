//
//  EmailSend.m
//  EmailTestProjectTests
//
//  Created by Kunal on 25/06/25.
//  Copyright © 2025 Facebook. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <XCTest/XCTest.h>
#import <Security/Security.h>

@interface SendEmailTest : XCTestCase
@end

@implementation SendEmailTest {
    NSInputStream *inputStream;
    NSOutputStream *outputStream;
}

- (void)testSendRealEmail {
    NSString *senderEmail = @"kunal.testkesh@gmail.com";
    NSString *receiverEmail = @"kunal.kesh@opkey.com";
    NSString *appPassword = @"bnwu jtkk vvwv wrsk";
    NSString *subject = @" Test Email from Objective-C (Mac)";
    NSString *body = @"This is a test email sent using Objective-C without any library.";

    [self sendEmailFrom:senderEmail to:receiverEmail subject:subject body:body password:appPassword];
}

- (void)sendEmailFrom:(NSString *)sender
                   to:(NSString *)recipient
              subject:(NSString *)subject
                 body:(NSString *)body
             password:(NSString *)appPassword {
    
  NSString *host = @"smtp.gmail.com";
  NSInteger port = 587;

  NSInputStream *inStream = nil;
  NSOutputStream *outStream = nil;
  [NSStream getStreamsToHostWithName:host port:port inputStream:&inStream outputStream:&outStream];
  inputStream = inStream;
  outputStream = outStream;

  [inputStream open];
  [outputStream open];

    [self readResponse]; // Greet
    [self sendCommand:@"EHLO localhost\r\n"];
    [self readResponse];

    [self sendCommand:@"STARTTLS\r\n"];
    [self readResponse];

    // Secure the stream (TLS)
    NSDictionary *sslSettings = @{ (NSString *)kCFStreamSSLLevel : (NSString *)kCFStreamSocketSecurityLevelNegotiatedSSL };
    CFReadStreamSetProperty((CFReadStreamRef)inputStream, kCFStreamPropertySSLSettings, (__bridge CFTypeRef)sslSettings);
    CFWriteStreamSetProperty((CFWriteStreamRef)outputStream, kCFStreamPropertySSLSettings, (__bridge CFTypeRef)sslSettings);

    [self sendCommand:@"EHLO localhost\r\n"];
    [self readResponse];

    // AUTH LOGIN
    [self sendCommand:@"AUTH LOGIN\r\n"];
    [self readResponse];

    [self sendBase64:sender];
    [self sendCommand:@"\r\n"];
    [self readResponse];

    [self sendBase64:appPassword];
    [self sendCommand:@"\r\n"];
    [self readResponse];

    // MAIL FROM
    [self sendCommand:[NSString stringWithFormat:@"MAIL FROM:<%@>\r\n", sender]];
    [self readResponse];

    // RCPT TO
    [self sendCommand:[NSString stringWithFormat:@"RCPT TO:<%@>\r\n", recipient]];
    [self readResponse];

    // DATA
    [self sendCommand:@"DATA\r\n"];
    [self readResponse];

    NSString *emailData = [NSString stringWithFormat:
        @"From: %@\r\nTo: %@\r\nSubject: %@\r\nContent-Type: text/plain; charset=utf-8\r\n\r\n%@\r\n.\r\n",
        sender, recipient, subject, body];

    [self sendCommand:emailData];
    [self readResponse];

    [self sendCommand:@"QUIT\r\n"];
    [self readResponse];

    [inputStream close];
    [outputStream close];

    NSLog(@"Email successfully sent.");
}

- (void)sendCommand:(NSString *)cmd {
    NSData *data = [cmd dataUsingEncoding:NSUTF8StringEncoding];
    [outputStream write:data.bytes maxLength:data.length];
    [NSThread sleepForTimeInterval:0.3];
}

- (void)sendBase64:(NSString *)string {
    NSData *data = [string dataUsingEncoding:NSUTF8StringEncoding];
    NSString *b64 = [data base64EncodedStringWithOptions:0];
    [self sendCommand:b64];
}

- (void)readResponse {
    uint8_t buffer[1024];
    NSInteger len = [inputStream read:buffer maxLength:sizeof(buffer)];
    if (len > 0) {
        NSString *response = [[NSString alloc] initWithBytes:buffer length:len encoding:NSUTF8StringEncoding];
        NSLog(@"SMTP: %@", response);
    }
}

@end
