import type React from 'react';

// Define types for our data based on the API schema
export interface Session {
  session: number;
  name: string;
}

interface SessionDropdownProps {
  sessions: Session[];
  selectedSession: number | null;
  onSessionChange: (session: number) => void;
}

export const SessionDropdown: React.FC<SessionDropdownProps> = ({
  sessions,
  selectedSession,
  onSessionChange,
}) => {
  return (
    <div className="mb-4">
      <label htmlFor="session-select" className="font-semibold mr-2">
        回次:
      </label>
      <select
        id="session-select"
        value={selectedSession || ''}
        onChange={(e) => onSessionChange(Number(e.target.value))}
        className="border rounded p-2 bg-white dark:bg-gray-700 dark:text-gray-100"
      >
        {sessions.map((s) => (
          <option key={s.session} value={s.session}>
            {s.name}
          </option>
        ))}
      </select>
    </div>
  );
};

interface MeetingNameDropdownProps {
    meetingNames: string[];
    selectedMeetingName: string | null;
    onMeetingNameChange: (name: string) => void;
    disabled: boolean;
}

export const MeetingNameDropdown: React.FC<MeetingNameDropdownProps> = ({
    meetingNames,
    selectedMeetingName,
    onMeetingNameChange,
    disabled,
}) => {
    return (
        <div className="mb-4">
            <label htmlFor="meeting-name-select" className="font-semibold mr-2">
                会議名:
            </label>
            <select
                id="meeting-name-select"
                value={selectedMeetingName || ''}
                onChange={(e) => onMeetingNameChange(e.target.value)}
                disabled={disabled}
                className="border rounded p-2 bg-white dark:bg-gray-700 dark:text-gray-100"
            >
                <option value="">全て</option>
                {meetingNames.map((name) => (
                    <option key={name} value={name}>
                        {name}
                    </option>
                ))}
            </select>
        </div>
    );
}