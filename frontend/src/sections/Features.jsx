/* src/sections/Features.jsx */
export default function Features() {
    return (
      <section className="py-5 bg-light">
        <div className="container">
          <div className="row g-5">
            {/* left column intro */}
            <div className="col-lg-3">
              <h2 className="fw-bold mb-3">Enhance University Guidance</h2>
              <p className="text-muted">
                UniAdvisor provides tools to save time, stay organized, and offer improved guidance
                to undergraduates, postgraduates, and international applicants.
              </p>
            </div>
  
            {/* right column card grid */}
            <div className="col-lg-9">
              <div className="row g-4">
                {cards.map(card => (
                  <div key={card.title} className="col-md-6">
                    <div className="card h-100 shadow-sm border-0">
                      <img src={card.img} className="card-img-top" alt={card.title} />
                      <div className="card-body">
                        <h5 className="card-title fw-semibold">{card.title}</h5>
                        <p className="card-text">{card.text}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>
    );
  }
  
  const cards = [
    {
      title: 'Efficient Application Reviews',
      text: 'Simplify and streamline the application review process, allowing advisors to focus on quality guidance rather than administrative tasks.',
      //img: '/images/feature-apply.jpg',
    },
    {
      title: 'Event Management Made Easy',
      text: 'Manage university events seamlessly within the platform, ensuring advisors can coordinate and track important admissions events.',
      //img: '/images/feature-events.jpg',
    },
    {
      title: 'Track Student Progress',
      text: 'Monitor and track student progress effectively, ensuring nothing slips through the cracks.',
      //img: '/images/feature-progress.jpg',
    },
    {
      title: 'Comprehensive Guidance Tools',
      text: 'UniAdvisor offers a comprehensive set of tools tailored for admissions advisors and consultants.',
      //img: '/images/feature-tools.jpg',
    },
  ];
  