import { TestBed } from '@angular/core/testing';

import { Record } from './record';

describe('Record', () => {
  let service: Record;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Record);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
