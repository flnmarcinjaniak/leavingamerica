import React from 'react';
import { Composition } from 'remotion';
import {
  CountryPin, CityPin, ListPin, ContrastPin,
  PW, PH,
  type CountryPinProps, type CityPinProps, type ListPinProps, type ContrastPinProps,
} from './PinLayouts';

/* Pins are stills; duration/fps are formalities Remotion requires. */
const still = { durationInFrames: 1, fps: 1, width: PW, height: PH };

export const PinRoot: React.FC = () => (
  <>
    <Composition
      id="pin-country"
      component={CountryPin}
      {...still}
      defaultProps={{
        name: 'Portugal', bg: 'lisbon', monthly: 2100, years: 4.0,
        health: 8, safety: 8, visa: 90, nomad: true,
      } satisfies CountryPinProps}
    />
    <Composition
      id="pin-city"
      component={CityPin}
      {...still}
      defaultProps={{
        city: 'Batumi', country: 'Georgia', bg: 'batumi', monthly: 350, years: 23.8,
      } satisfies CityPinProps}
    />
    <Composition
      id="pin-list"
      component={ListPin}
      {...still}
      defaultProps={{
        eyebrow: 'ranking', title: 'Cheap countries that are actually safe',
        bg: 'danang', accent: '#34D399',
        rows: [
          { left: 'Vietnam', right: '9.3 yrs' },
          { left: 'Malaysia', right: '7.9 yrs' },
          { left: 'Romania', right: '7.2 yrs' },
          { left: 'Bulgaria', right: '7.2 yrs' },
          { left: 'Montenegro', right: '6.9 yrs' },
        ],
      } satisfies ListPinProps}
    />
    <Composition
      id="pin-contrast"
      component={ContrastPin}
      {...still}
      defaultProps={{
        eyebrow: 'the visa trap', title: 'You can afford it. You cannot stay.',
        bg: 'cairo',
        a: { label: 'What $100,000 buys', value: '11.9 years' },
        b: { label: 'What the visa allows', value: '30 days' },
        note: '10 of 74 countries do exactly this',
      } satisfies ContrastPinProps}
    />
  </>
);
