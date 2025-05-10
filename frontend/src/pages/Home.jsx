// src/pages/Home.jsx
import { useState } from 'react';
import Hero from '../sections/Hero';
import SignInModal from '../components/SignInModal';
import SignUpModal from '../components/SignUpModal';
import GuidanceSection from '../components/GuidanceSection';

export default function Home() {
  const [modal, setModal] = useState(null);   // null | 'signin' | 'signup'
  console.log('modal state:', modal);
  return (
    <>
      <Hero
        onSignIn={() => setModal('signin')}
        onSignUp={() => setModal('signup')}
      />
    {/* NEW – feature / guidance block */}
        <GuidanceSection />
      {modal === 'signin' && <SignInModal onClose={() => setModal(null)} />}
      {modal === 'signup' && <SignUpModal onClose={() => setModal(null)} />}
    </>
  );
}

