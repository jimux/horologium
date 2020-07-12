import { Component, OnInit } from '@angular/core';
import { UserService } from './user.service';
import { ClockdataService } from './clockdata.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.sass']
})
export class AppComponent implements OnInit {
  title = 'Horologium';

  constructor(
    private userService: UserService,
    private clockService: ClockdataService
  ) {}

  ngOnInit(): void {
  }
}
