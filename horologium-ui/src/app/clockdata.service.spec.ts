import { TestBed } from '@angular/core/testing';

import { ClockdataService } from './clockdata.service';

describe('ClockdataService', () => {
  let service: ClockdataService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ClockdataService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
