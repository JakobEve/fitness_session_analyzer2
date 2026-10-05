class Participant:
    def __init__(self,participant_id,baseline_heart_rate,baseline_skin_response,baseline_temperature):
        if baseline_heart_rate<30 or baseline_heart_rate>120:
            raise ValueError("baseline_heart_rate outside of values 30-120")
        if baseline_skin_response<0:
            raise ValueError("baseline_skin_response cant be ngeative")
        if baseline_temperature<25 or baseline_temperature>42:
            raise ValueError("baseline_temperature outside of values 25-42")

        self.__participant_id=participant_id
        self.__baseline_heart_rate=baseline_heart_rate
        self.__baseline_skin_response=baseline_skin_response
        self.__baseline_temperature=baseline_temperature

    def get_participant_id(self):
        return self.__participant_id

    def get_baseline_heart_rate(self):
        return self.__baseline_heart_rate

    def get_baseline_skin_response(self):
        return self.__baseline_skin_response

    def get_baseline_temperature(self):
        return self.__baseline_temperature

    @classmethod
    def from_profile_dict(cls,profile):
        return cls(
            profile["participant_id"],
            profile["baseline_heart_rate"],
            profile["baseline_skin_response"],
            profile["baseline_temperature"]
        )



class Observation:
    def __init__(self,timestamp,heart_rate,skin_response,temperature,activity_level, signal_quality):
        self.__timestamp=timestamp
        self.__heart_rate=heart_rate
        self.__skin_response=skin_response
        self.__temperature=temperature
        self.__activity_level=activity_level
        self.__signal_quality=signal_quality
        self.__valid=self.__check_valid()
    def __check_valid(self):
        if self.__heart_rate is None or self.__heart_rate<35 or self.__heart_rate>205:
            return False
        if self.__skin_response is None or self.__skin_response<0:
            return False
        if self.__temperature is None or self.__temperature<25 or self.__temperature>42:
            return False
        if self.__activity_level is None or self.__activity_level<0 or self.__activity_level>1:
            return False
        if self.__signal_quality is None or self.__signal_quality<0 or self.__signal_quality>1:
            return False
        return True
    def get_timestamp(self):
        return self.__timestamp
    def get_heart_rate(self):
        return self.__heart_rate
    def get_skin_response(self):
        return self.__skin_response
    def get_temperature(self):
        return self.__temperature
    def get_activity_level(self):
        return self.__activity_level
    def get_signal_quality(self):
        return self.__signal_quality
    def get_is_valid(self):
        return self.__valid

    @classmethod
    def from_observation_dicts(cls,data):
        return cls(
            data["timestamp"],
            data["heart_rate"],
            data["skin_response"],
            data["temperature"],
            data["activity_level"],
            data["signal_quality"],
        )

class Session:
    def __init__(self,participant,observations):
        self.__participant=participant
        self.__observations=observations
    def get_participant(self):
        return self.__participant
    def get_observations(self):
        return self.__observations

    def get_valid_observations(self):
        valid=[]
        for observation in self.__observations:
            if observation.get_is_valid():
                valid.append(observation)
        return valid
    def get_usable_count(self):
        return len(self.get_valid_observations())
    def get_total_count(self):
        return len(self.__observations)

    @classmethod
    def from_raw_data(cls,profile,raw_observations):
        participant=Participant.from_profile_dict(profile)

        observations=[]
        for raw in raw_observations:
            observations.append(Observation.from_observation_dicts(raw))

        return cls(participant, observations)

def compute_summary(values):
    if len(values)==0:
        return {"average": None, "minimum": None, "maximum": None}
    total = 0
    for value in values:
        total=total+value
    average=total/len(values)
    return{
        "average": round(average,2),
        "minimum": min(values),
        "maximum": max(values),
    }

def compare_to_baseline(observed_average, baseline_value):
    return round(observed_average-baseline_value,2)

def detect_recovery(values):
    if len(values)<4:
        return False
    half = len(values)//2
    first_average=sum(values[:half])/len(values[:half])
    second_average=sum(values[half:])/len(values[half:])
    decline=first_average-second_average
    return decline>10


class SessionAnalyzer:
    MINIMUM_VALID_OBSERVATIONS=3
    def __init__(self,session):
        self.__session=session

    def analyze(self):
        valid_observations=self.__session.get_valid_observations()
        total_count=self.__session.get_total_count()
        usable_count=len(valid_observations)

        if usable_count<self.MINIMUM_VALID_OBSERVATIONS:
            return {
                "participant_id": self.__session.get_participant().get_participant_id(),
                "total_count": total_count,
                "usable_count": usable_count,
                "classification": "insufficient data",
                "explanation": "too few valid observations to analyze the session",
            }

        heart_rates=[]
        activity_levels=[]
        for observation in valid_observations:
            heart_rates.append(observation.get_heart_rate())
            activity_levels.append(observation.get_activity_level())

        heart_rate_summary=compute_summary(heart_rates)
        activity_summary=compute_summary(activity_levels)

        baseline_heart_rate = self.__session.get_participant().get_baseline_heart_rate()
        heart_rate_vs_baseline=compare_to_baseline(heart_rate_summary["average"],baseline_heart_rate)
        is_recovering=detect_recovery(heart_rates)

        classification, explanation = self.__classify(heart_rate_vs_baseline, is_recovering)

        return {
            "participant_id": self.__session.get_participant().get_participant_id(),
            "total_count": total_count,
            "usable_count": usable_count,
            "heart_rate_summary": heart_rate_summary,
            "activity_summary": activity_summary,
            "heart_rate_vs_baseline": heart_rate_vs_baseline,
            "is_recovering": is_recovering,
            "classification": classification,
            "explanation": explanation,
        }
    def __classify(self, heart_rate_vs_baseline, is_recovering):
        if is_recovering and heart_rate_vs_baseline>15:
            return "recovering", "Heart rate is falling toward baseline after elevated activity"
        if heart_rate_vs_baseline<15:
            return "resting", "Heart rate is close to the participants basline"
        if heart_rate_vs_baseline<=45:
            return "moderate activity", "Heart rate is moderately elevated above baseline"
        return "high activity", "heart rate is very elevated above baseline"


def analyze_sessions(sessions, participants):
    results = []
    for session_id, data in sessions.items():
        participant = participants[data["participant_id"]]
        observations = [Observation.from_observation_dicts(row) for row in data["observations"]]
        result = SessionAnalyzer(Session(participant, observations)).analyze()
        result["session_id"] = session_id
        results.append(result)
    return results
