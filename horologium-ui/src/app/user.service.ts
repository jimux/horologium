import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

interface IHttpOptions {
  headers: HttpHeaders;
}

@Injectable()
export class UserService {
  private httpOptions: IHttpOptions;
  public token: string;
  public username: string;
  public errors: any = [];

  constructor(private http: HttpClient) {
    this.httpOptions = {
      headers: new HttpHeaders({ 'Content-Type': 'application/json' })
    };
  }

  public login(username: string, password: string): void {
    this.username = username;
    this.http
      .post(
        '/token-auth/',
        JSON.stringify({
          username: username,
          password: password
        }),
        this.httpOptions
      )
      .subscribe(
        (data) => {
          this.token = data['token'];
          this.errors = [];
        },
        (err) => {
          this.errors = err['error'];
        }
      );
  }

  public logout(): void {
    this.token = null;
  }
}
