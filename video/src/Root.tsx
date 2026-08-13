import React from 'react';
import { Composition } from 'remotion';
import { VisaTrap, TOTAL_FRAMES as F1 } from './VisaTrap';
import { FireNumber, TOTAL_FRAMES as F2 } from './FireNumber';
import { HalfPrice, TOTAL_FRAMES as F3 } from './HalfPrice';
import { Dangerous, TOTAL_FRAMES as F4 } from './Dangerous';
import { Income, TOTAL_FRAMES as F5 } from './Income';
import { Rent, TOTAL_FRAMES as F6 } from './Rent';
import { FPS, W, H } from './theme';

const base = { fps: FPS, width: W, height: H };

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="visa-trap"   component={VisaTrap}   durationInFrames={F1} {...base} />
    <Composition id="fire-number" component={FireNumber} durationInFrames={F2} {...base} />
    <Composition id="half-price"  component={HalfPrice}  durationInFrames={F3} {...base} />
    <Composition id="dangerous"   component={Dangerous}  durationInFrames={F4} {...base} />
    <Composition id="income"      component={Income}     durationInFrames={F5} {...base} />
    <Composition id="rent"        component={Rent}       durationInFrames={F6} {...base} />
  </>
)
