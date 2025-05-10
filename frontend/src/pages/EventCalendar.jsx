import React, { useEffect, useState } from "react";

import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';


export default function EventCalendar() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    fetch("/api/events/")
      .then((res) => res.json())
      .then((data) => {
        const formattedEvents = data.map((event) => ({
          id: event.id,
          title: event.title,
          start: event.date,
          extendedProps: {
            description: event.description,
            created_by: event.created_by,
            members: event.members.join(", "),
          },
        }));
        setEvents(formattedEvents);
      });
  }, []);

  const handleEventClick = (info) => {
    const { title, extendedProps } = info.event;
    alert(
      `Event: ${title}\n` +
      `Description: ${extendedProps.description}\n` +
      `Host ID: ${extendedProps.created_by}\n` +
      `Members: ${extendedProps.members}`
    );
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-semibold mb-4">Upcoming Events</h2>
      <FullCalendar
        plugins={[dayGridPlugin]}
        initialView="dayGridMonth"
        events={events}
        height={600}
        eventClick={handleEventClick}
      />
    </div>
  );
}
